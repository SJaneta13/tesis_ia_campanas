# dashboard/data_loader.py
from pathlib import Path
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]

DATA_SURVEY = ROOT / "data" / "processed" / "encuestas" / "model_ready.csv"

NEWS_CASES = {
    "case1_es": ROOT / "outputs" / "text_analysis" / "case1_es" / "news_sentiment_scored.csv",
    "case2_en": ROOT / "outputs" / "text_analysis" / "case2_en" / "news_sentiment_scored.csv",
    "case3_ec_media": ROOT / "outputs" / "text_analysis" / "case3_ec_media" / "news_sentiment_scored.csv",
}

METRICS_DIR = ROOT / "outputs" / "latest" / "tables"


@st.cache_data
def load_survey() -> pd.DataFrame:
    if not DATA_SURVEY.exists():
        return pd.DataFrame()

    return pd.read_csv(DATA_SURVEY, encoding="utf-8-sig")


@st.cache_data
def load_news_cases() -> pd.DataFrame:
    frames = []

    for case_id, path in NEWS_CASES.items():
        if path.exists():
            df = pd.read_csv(path, encoding="utf-8-sig")
            df["case_id"] = case_id
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


@st.cache_data
def load_latest_metrics() -> pd.DataFrame:
    if not METRICS_DIR.exists():
        return pd.DataFrame()

    files = sorted(METRICS_DIR.glob("metrics_run_*.csv"))

    if not files:
        return pd.DataFrame()

    return pd.read_csv(files[-1], encoding="utf-8-sig")


@st.cache_data
def load_latest_seed_metrics() -> pd.DataFrame:
    if not METRICS_DIR.exists():
        return pd.DataFrame()

    files = sorted(METRICS_DIR.glob("metrics_by_seed_*.csv"))

    if not files:
        return pd.DataFrame()

    return pd.read_csv(files[-1], encoding="utf-8-sig")