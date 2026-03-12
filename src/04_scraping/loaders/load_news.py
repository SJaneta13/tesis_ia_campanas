from __future__ import annotations
from pathlib import Path
import pandas as pd


CANONICAL_COLS = [
    "platform", "source", "source_id", "url",
    "published_at", "date", "language", "title", "text",
    "query", "case_id", "run_id", "stage", "is_ai_related"
]

def load_news_folder(news_dir: str | Path) -> pd.DataFrame:
    news_dir = Path(news_dir)
    files = sorted(news_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No se encontraron CSVs en: {news_dir}")

    dfs = [pd.read_csv(f) for f in files]
    df = pd.concat(dfs, ignore_index=True)

    out = pd.DataFrame({
        "platform": df.get("platform", "news_gdelt"),
        "source": df.get("domain", df.get("source", pd.NA)),
        "source_id": df.get("source_id", pd.NA),
        "url": df.get("url", pd.NA),
        "published_at": df.get("published_at", df.get("seendate", pd.NA)),
        "date": pd.to_datetime(df.get("date", df.get("published_at", pd.NA)), errors="coerce"),
        "language": df.get("language", df.get("lang", pd.NA)),
        "title": df.get("title", pd.NA),
        "text": df.get("text", pd.NA),
        "query": df.get("query", pd.NA),
        "case_id": df.get("case_id", pd.NA),
        "run_id": df.get("run_id", pd.NA),
        "stage": df.get("stage", pd.NA),
        "is_ai_related": df.get("is_ai_related", pd.NA),
    })

    # asegurar columnas
    for c in CANONICAL_COLS:
        if c not in out.columns:
            out[c] = pd.NA

    return out[CANONICAL_COLS]