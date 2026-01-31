# src/04_scraping/text_utils.py
from __future__ import annotations

import re
import pandas as pd
from .config import IA_REGEX, CANDIDATE_NOB, CANDIDATE_LUI


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"http\S+", " ", text)   # URLs
    text = re.sub(r"@\w+", " ", text)      # menciones
    text = re.sub(r"\s+", " ", text).strip()
    return text


def add_tags(df: pd.DataFrame) -> pd.DataFrame:
    df["text_clean"] = df["text"].fillna("").apply(clean_text)
    df["text_length"] = df["text_clean"].str.len()

    df["has_ia_terms"] = df["text_clean"].str.contains(IA_REGEX, regex=True, na=False)

    nob = df["text_clean"].str.contains(CANDIDATE_NOB, regex=True, na=False)
    lui = df["text_clean"].str.contains(CANDIDATE_LUI, regex=True, na=False)

    df["candidate_tag"] = "other"
    df.loc[nob & ~lui, "candidate_tag"] = "noboa"
    df.loc[lui & ~nob, "candidate_tag"] = "luisa"
    df.loc[nob & lui, "candidate_tag"] = "both"

    df["month"] = pd.to_datetime(df["date"], errors="coerce").dt.to_period("M").astype(str)
    return df
