# src/04_scraping/loaders/load_x.py
from __future__ import annotations
from snscrape.base import ScraperException
from pathlib import Path
import pandas as pd

STANDARD_COLS = [
    "source", "source_id", "url", "date", "author", "text",
    "lang", "engagement", "likeCount", "retweetCount", "replyCount", "quoteCount",
    "query"
]


def load_x_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["platform"] = "x"
    df["published_at"] = df["date"].astype(str)
    df["language"] = df["lang"]
    df["source"] = "x"


    df = df.rename(columns={
        "tweet_id": "source_id",
        "created_at": "date",
        "username": "author",
        "content": "text",
    })

    df["source"] = "x"
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for c in ["likeCount", "retweetCount", "replyCount", "quoteCount"]:
        if c not in df.columns:
            df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["engagement"] = df["likeCount"] + df["retweetCount"] + df["replyCount"] + df["quoteCount"]

    # asegurar columnas
    for col in STANDARD_COLS:
        if col not in df.columns:
            df[col] = None

    return df[STANDARD_COLS]

