from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ml_pipeline.src.models.item_based_cf import ItemBasedCFRecommender


@dataclass(frozen=True)
class RankingMetrics:
    num_users: int
    hit_rate_at_k: float
    recall_at_k: float


def evaluate_leave_one_out(
    recommender: ItemBasedCFRecommender,
    test: pd.DataFrame,
    top_k: int = 10,
    max_users: int | None = None,
) -> RankingMetrics:
    if max_users is not None:
        test = test.head(max_users).copy()

    hits = 0
    total = len(test)

    for row in test.itertuples(index=False):
        recommendations = recommender.recommend(int(row.user_id), top_k=top_k)
        if int(row.book_id) in recommendations:
            hits += 1

    metric = hits / total if total else 0.0
    return RankingMetrics(
        num_users=total,
        hit_rate_at_k=metric,
        recall_at_k=metric,
    )

