from __future__ import annotations

from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from scipy import sparse


class ItemBasedCFRecommender:
    def __init__(self, top_neighbors: int = 50) -> None:
        self.top_neighbors = top_neighbors
        self.user_items: dict[int, tuple[int, ...]] = {}
        self.item_popularity: Counter[int] = Counter()
        self.popular_items: list[int] = []
        self.item_neighbors: dict[int, list[tuple[int, float]]] = {}

    def fit(self, interactions: pd.DataFrame) -> "ItemBasedCFRecommender":
        grouped = interactions.groupby("user_id")["book_id"].agg(list)
        self.user_items = {
            int(user_id): tuple(dict.fromkeys(int(book_id) for book_id in items))
            for user_id, items in grouped.items()
        }

        user_ids = list(self.user_items)
        max_book_id = max(
            book_id
            for items in self.user_items.values()
            for book_id in items
        )

        row_indices: list[int] = []
        col_indices: list[int] = []
        data: list[int] = []
        for row_idx, user_id in enumerate(user_ids):
            for book_id in self.user_items[user_id]:
                row_indices.append(row_idx)
                col_indices.append(book_id - 1)
                data.append(1)

        user_item = sparse.csr_matrix(
            (data, (row_indices, col_indices)),
            shape=(len(user_ids), max_book_id),
            dtype=np.float32,
        )
        item_user = user_item.tocsc()

        item_support = np.asarray(user_item.sum(axis=0)).ravel()
        active_item_indices = np.flatnonzero(item_support)

        self.item_popularity = Counter(interactions["book_id"].astype(int).tolist())
        self.popular_items = [item for item, _ in self.item_popularity.most_common()]
        self.item_neighbors = {}

        for item_idx in active_item_indices:
            start = item_user.indptr[item_idx]
            end = item_user.indptr[item_idx + 1]
            user_rows = item_user.indices[start:end]
            if len(user_rows) == 0:
                self.item_neighbors[item_idx + 1] = []
                continue

            co_counts = np.asarray(user_item[user_rows].sum(axis=0)).ravel()
            co_counts[item_idx] = 0.0

            candidate_indices = np.flatnonzero(co_counts)
            if len(candidate_indices) == 0:
                self.item_neighbors[item_idx + 1] = []
                continue

            similarities = co_counts[candidate_indices] / np.sqrt(
                item_support[item_idx] * item_support[candidate_indices]
            )

            if len(candidate_indices) > self.top_neighbors:
                top_idx = np.argpartition(similarities, -self.top_neighbors)[
                    -self.top_neighbors :
                ]
                candidate_indices = candidate_indices[top_idx]
                similarities = similarities[top_idx]

            order = np.argsort(similarities)[::-1]
            self.item_neighbors[item_idx + 1] = [
                (int(candidate_indices[idx] + 1), float(similarities[idx]))
                for idx in order
            ]

        return self

    def recommend(self, user_id: int, top_k: int = 10) -> list[int]:
        seen_items = set(self.user_items.get(user_id, ()))
        scores: defaultdict[int, float] = defaultdict(float)

        for history_item in seen_items:
            for candidate_item, similarity in self.item_neighbors.get(history_item, []):
                if candidate_item in seen_items:
                    continue
                scores[candidate_item] += similarity

        ranked_candidates = sorted(
            scores.items(),
            key=lambda item: (item[1], self.item_popularity[item[0]], -item[0]),
            reverse=True,
        )
        recommendations = [item_id for item_id, _ in ranked_candidates[:top_k]]

        if len(recommendations) < top_k:
            for item_id in self.popular_items:
                if item_id in seen_items or item_id in recommendations:
                    continue
                recommendations.append(item_id)
                if len(recommendations) == top_k:
                    break

        return recommendations

