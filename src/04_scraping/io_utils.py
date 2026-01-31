# src/04_scraping/io_utils.py
from __future__ import annotations

from pathlib import Path
import pandas as pd


def read_csv_folder(folder: str | Path, pattern: str = "*.csv") -> list[Path]:
    folder = Path(folder)
    files = sorted(folder.glob(pattern))
    return files


def concat_dfs(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def ensure_parent(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
