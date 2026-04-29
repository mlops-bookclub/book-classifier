from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from ml_pipeline.src.datasets.goodbooks import (
    DEFAULT_RATINGS_PATH,
    load_positive_ratings,
    make_leave_one_out_split,
)
from ml_pipeline.src.evaluation.ranking_metrics import evaluate_leave_one_out
from ml_pipeline.src.models.item_based_cf import ItemBasedCFRecommender


DEFAULT_OUTPUT_PATH = Path("models/metrics/item_based_cf_baseline.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the first item-based collaborative filtering baseline."
    )
    parser.add_argument(
        "--ratings-path",
        type=Path,
        default=DEFAULT_RATINGS_PATH,
        help="Path to the Goodbooks ratings CSV.",
    )
    parser.add_argument(
        "--min-rating",
        type=int,
        default=4,
        help="Minimum rating treated as a positive interaction.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of books to recommend for each user.",
    )
    parser.add_argument(
        "--max-users",
        type=int,
        default=None,
        help="Optional cap for evaluation users during development.",
    )
    parser.add_argument(
        "--top-neighbors",
        type=int,
        default=50,
        help="Number of similar books to keep per book.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Where to save the baseline metrics JSON.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    ratings = load_positive_ratings(
        ratings_path=args.ratings_path,
        min_rating=args.min_rating,
    )
    split = make_leave_one_out_split(ratings)

    recommender = ItemBasedCFRecommender(top_neighbors=args.top_neighbors).fit(split.train)
    metrics = evaluate_leave_one_out(
        recommender=recommender,
        test=split.test,
        top_k=args.top_k,
        max_users=args.max_users,
    )

    payload = {
        "model": "item_based_cf",
        "ratings_path": str(args.ratings_path),
        "min_rating": args.min_rating,
        "top_k": args.top_k,
        "top_neighbors": args.top_neighbors,
        "train_interactions": int(len(split.train)),
        "test_interactions": int(len(split.test)),
        **asdict(metrics),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

