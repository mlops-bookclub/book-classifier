from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DEFAULT_RATINGS_PATH = Path("../../../data/raw/goodbooks-10k/ratings.csv")


@dataclass(frozen=True)
class LeaveOneOutSplit:
    train: pd.DataFrame
    test: pd.DataFrame


def load_positive_ratings(
        ratings_path: str | Path = DEFAULT_RATINGS_PATH,
        min_rating: int = 4,
) -> pd.DataFrame:
    ratings = pd.read_csv(ratings_path, usecols=["user_id", "book_id", "rating"])
    ratings = ratings[ratings["rating"] >= min_rating].copy()
    ratings["event_idx"] = range(len(ratings))
    return ratings


def make_leave_one_out_split(ratings: pd.DataFrame) -> LeaveOneOutSplit:
    eligible = ratings.groupby("user_id").filter(lambda group: len(group) >= 2).copy()
    eligible = eligible.sort_values(["user_id", "event_idx"])

    test_idx = eligible.groupby("user_id", sort=False).tail(1).index
    test = eligible.loc[test_idx, ["user_id", "book_id", "rating", "event_idx"]].copy()
    train = eligible.drop(index=test_idx).copy()

    return LeaveOneOutSplit(
        train=train.reset_index(drop=True),
        test=test.reset_index(drop=True),
    )

