import pandas as pd

from ml_pipeline.src.datasets.goodbooks import make_leave_one_out_split
from ml_pipeline.src.evaluation.ranking_metrics import evaluate_leave_one_out
from ml_pipeline.src.models.item_based_cf import ItemBasedCFRecommender


def test_leave_one_out_baseline_evaluates_all_users() -> None:
    ratings = pd.DataFrame(
        [
            {"user_id": 1, "book_id": 1, "rating": 5, "event_idx": 0},
            {"user_id": 1, "book_id": 2, "rating": 4, "event_idx": 1},
            {"user_id": 2, "book_id": 1, "rating": 5, "event_idx": 2},
            {"user_id": 2, "book_id": 2, "rating": 4, "event_idx": 3},
            {"user_id": 3, "book_id": 1, "rating": 5, "event_idx": 4},
            {"user_id": 3, "book_id": 3, "rating": 4, "event_idx": 5},
        ]
    )

    split = make_leave_one_out_split(ratings)
    recommender = ItemBasedCFRecommender(top_neighbors=2).fit(split.train)
    metrics = evaluate_leave_one_out(recommender, split.test, top_k=1)

    assert metrics.num_users == 3
    assert len(split.train) == 3
    assert len(split.test) == 3
    assert 0.0 <= metrics.hit_rate_at_k <= 1.0
    assert 0.0 <= metrics.recall_at_k <= 1.0
