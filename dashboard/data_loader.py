from pathlib import Path
import pandas as pd
import streamlit as st
import sys


# =========================================================
# Rutas principales del proyecto
# =========================================================
ROOT = Path(__file__).resolve().parents[1]

DATA_SURVEY = ROOT / "data" / "processed" / "encuestas" / "model_ready.csv"

NEWS_CASES = {
    "case1_es": ROOT / "outputs" / "text_analysis" / "case1_es" / "news_sentiment_scored.csv",
    "case2_en": ROOT / "outputs" / "text_analysis" / "case2_en" / "news_sentiment_scored.csv",
    "case3_ec_media": ROOT / "outputs" / "text_analysis" / "case3_ec_media" / "news_sentiment_scored.csv",
}

SOCIAL_SENTIMENT_PATH = ROOT / "outputs" / "text_analysis" / "social_x" / "social_sentiment_scored.csv"

METRICS_DIR = ROOT / "outputs" / "latest" / "tables"

SURVEY_PUBLIC = ROOT / "backend" / "public" / "surveys"

RISK_INDEX_BY_AGE = SURVEY_PUBLIC / "tables" / "risk_index_by_age.csv"
DEEPFAKE_DISTRUST_BY_AGE = SURVEY_PUBLIC / "tables" / "deepfake_distrust_by_age.csv"
EXPOSURE_INDEX_BY_AGE = SURVEY_PUBLIC / "tables" / "exposure_index_by_age.csv"
EXPOSURE_INDEX_BY_AGE_ROBUST = SURVEY_PUBLIC / "tables" / "exposure_index_by_age_robust.csv"


# =========================================================
# Artefactos técnicos para trazabilidad del dashboard
# =========================================================

DATA_QUALITY_REPORT = METRICS_DIR / "data_quality_report.csv"
VARIABLE_DICTIONARY = METRICS_DIR / "variable_dictionary.csv"
CONSTRUCT_MAP = METRICS_DIR / "construct_map.csv"
TRIANGULATION_MATRIX = METRICS_DIR / "triangulation_matrix.csv"
RECOMMENDATION_RULES = METRICS_DIR / "recommendation_rules.csv"

FEATURE_IMPORTANCE = METRICS_DIR / "feature_importance_latest.csv"
MODEL_COMPARISON = METRICS_DIR / "model_comparison_summary.csv"
CONFUSION_MATRIX_3 = METRICS_DIR / "confusion_matrix_3_levels.csv"
CONFUSION_MATRIX_5 = METRICS_DIR / "confusion_matrix_5_levels.csv"


MODEL_METRICS_SUMMARY = METRICS_DIR / "model_metrics_summary.csv"
MODEL_METRICS_BY_SEED = METRICS_DIR / "model_metrics_by_seed_dashboard.csv"
CONFUSION_MATRIX_3 = METRICS_DIR / "confusion_matrix_3_levels.csv"
CONFUSION_MATRIX_5 = METRICS_DIR / "confusion_matrix_5_levels.csv"
FEATURE_IMPORTANCE = METRICS_DIR / "feature_importance_latest.csv"
MODEL_INTERPRETATION = METRICS_DIR / "model_interpretation_rules.csv"
SIMULATOR_SCHEMA = METRICS_DIR / "simulator_feature_schema.csv"


MODEL_TABLES_DIR = ROOT / "outputs" / "latest" / "tables"
# =========================================================
# Lectura segura
# =========================================================

def read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin1")
    except Exception:
        return pd.DataFrame()



def _read_model_table(filename: str, fallback_filenames: list[str] | None = None) -> pd.DataFrame:
    """Lee artefactos del módulo de modelos desde outputs/latest/tables."""
    candidates = [filename] + (fallback_filenames or [])
    for name in candidates:
        path = MODEL_TABLES_DIR / name
        if not path.exists():
            continue
        try:
            return pd.read_csv(path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            return pd.read_csv(path, encoding="latin1")
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_model_metrics_summary() -> pd.DataFrame:
    return _read_model_table(
        "model_metrics_summary.csv",
        [
            "model_metrics_summary_latest.csv",
            "metrics_model_summary.csv",
            "model_comparison_summary.csv",
        ],
    )


@st.cache_data(show_spinner=False)
def load_model_metrics_by_seed_dashboard() -> pd.DataFrame:
    return _read_model_table(
        "model_metrics_by_seed_dashboard.csv",
        [
            "model_metrics_by_seed.csv",
            "seed_metrics_dashboard.csv",
            "model_seed_metrics.csv",
        ],
    )


@st.cache_data(show_spinner=False)
def load_confusion_matrix_3_levels() -> pd.DataFrame:
    return _read_model_table(
        "confusion_matrix_3_levels.csv",
        [
            "confusion_matrix_3niveles.csv",
            "confusion_3_levels.csv",
            "cm_3_levels.csv",
        ],
    )


@st.cache_data(show_spinner=False)
def load_confusion_matrix_5_levels() -> pd.DataFrame:
    return _read_model_table(
        "confusion_matrix_5_levels.csv",
        [
            "confusion_matrix_5niveles.csv",
            "confusion_5_levels.csv",
            "cm_5_levels.csv",
        ],
    )


@st.cache_data(show_spinner=False)
def load_feature_importance() -> pd.DataFrame:
    return _read_model_table(
        "feature_importance_latest.csv",
        [
            "feature_importance.csv",
            "model_feature_importance.csv",
            "feature_importances.csv",
        ],
    )


@st.cache_data(show_spinner=False)
def load_model_interpretation_rules() -> pd.DataFrame:
    return _read_model_table(
        "model_interpretation_rules.csv",
        [
            "model_interpretation.csv",
            "interpretation_rules.csv",
            "technical_interpretation_rules.csv",
        ],
    )


@st.cache_data(show_spinner=False)
def load_simulator_feature_schema() -> pd.DataFrame:
    return _read_model_table(
        "simulator_feature_schema.csv",
        [
            "model_simulator_schema.csv",
            "simulator_schema.csv",
            "prediction_simulator_schema.csv",
        ],
    )


# =========================================================
# Encuestas
# =========================================================

@st.cache_data(ttl=600)
def load_survey() -> pd.DataFrame:
    return read_csv_safe(DATA_SURVEY)


# =========================================================
# Evidencia digital / GDELT
# =========================================================
@st.cache_data
def load_news_cases() -> pd.DataFrame:
    frames = []

    def _normalize_sentiment_label(value):
        value = str(value or "").strip().lower()

        mapping = {
            "positive": "Positivo",
            "positivo": "Positivo",
            "pos": "Positivo",
            "neutral": "Neutral",
            "neu": "Neutral",
            "negative": "Negativo",
            "negativo": "Negativo",
            "neg": "Negativo",
        }

        return mapping.get(value, "No clasificado")

    def _read_file(path: Path, case_id: str, corpus_type: str) -> pd.DataFrame:
        df = pd.read_csv(path, encoding="utf-8-sig")

        df["case_id"] = case_id
        df["corpus_type"] = corpus_type

        # Normalización de columnas entre GDELT y redes
        if "source" not in df.columns and "domain" in df.columns:
            df["source"] = df["domain"]

        if "source" not in df.columns and "platform" in df.columns:
            df["source"] = df["platform"]

        if "text" not in df.columns and "content" in df.columns:
            df["text"] = df["content"]

        if "url" not in df.columns and "source_url" in df.columns:
            df["url"] = df["source_url"]

        if "date" not in df.columns and "published_at" in df.columns:
            df["date"] = df["published_at"]

        if "platform" not in df.columns:
            df["platform"] = "news_gdelt" if corpus_type == "news_gdelt" else "social_media"

        if "sentiment_label" not in df.columns:
            df["sentiment_label"] = pd.NA

        if "sentiment_score" not in df.columns:
            df["sentiment_score"] = pd.NA

        df["sentiment_label_std"] = df["sentiment_label"].apply(_normalize_sentiment_label)
        df["sentiment_score"] = pd.to_numeric(df["sentiment_score"], errors="coerce")

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Asegurar columnas mínimas para el dashboard
        required_cols = [
            "case_id", "corpus_type", "platform", "source", "url",
            "date", "title", "text", "sentiment_label",
            "sentiment_label_std", "sentiment_score"
        ]

        for col in required_cols:
            if col not in df.columns:
                df[col] = pd.NA

        return df

    for case_id, path in NEWS_CASES.items():
        if path.exists():
            frames.append(_read_file(path, case_id, "news_gdelt"))

    if SOCIAL_SENTIMENT_PATH.exists():
        frames.append(_read_file(SOCIAL_SENTIMENT_PATH, "social_x", "social_media"))

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True, sort=False)  


# =========================================================
# Métricas de modelado
# =========================================================

@st.cache_data(ttl=600)
def load_latest_metrics() -> pd.DataFrame:
    if not METRICS_DIR.exists():
        return pd.DataFrame()

    files = sorted(METRICS_DIR.glob("metrics_run_*.csv"))

    if not files:
        return pd.DataFrame()

    return read_csv_safe(files[-1])


@st.cache_data(ttl=600)
def load_latest_seed_metrics() -> pd.DataFrame:
    if not METRICS_DIR.exists():
        return pd.DataFrame()

    files = sorted(METRICS_DIR.glob("metrics_by_seed_*.csv"))

    if not files:
        return pd.DataFrame()

    return read_csv_safe(files[-1])


@st.cache_data(ttl=600)
def load_model_comparison_summary() -> pd.DataFrame:
    return read_csv_safe(MODEL_COMPARISON)


# =========================================================
# Tablas publicadas de encuestas
# =========================================================

@st.cache_data(ttl=600)
def load_risk_index_by_age() -> pd.DataFrame:
    return read_csv_safe(RISK_INDEX_BY_AGE)


@st.cache_data(ttl=600)
def load_deepfake_distrust_by_age() -> pd.DataFrame:
    return read_csv_safe(DEEPFAKE_DISTRUST_BY_AGE)


@st.cache_data(ttl=600)
def load_exposure_index_by_age() -> pd.DataFrame:
    return read_csv_safe(EXPOSURE_INDEX_BY_AGE)


@st.cache_data(ttl=600)
def load_exposure_index_by_age_robust() -> pd.DataFrame:
    return read_csv_safe(EXPOSURE_INDEX_BY_AGE_ROBUST)


# =========================================================
# Artefactos de trazabilidad
# =========================================================

@st.cache_data(ttl=600)
def load_data_quality_report() -> pd.DataFrame:
    return read_csv_safe(DATA_QUALITY_REPORT)


@st.cache_data(ttl=600)
def load_variable_dictionary() -> pd.DataFrame:
    return read_csv_safe(VARIABLE_DICTIONARY)


@st.cache_data(ttl=600)
def load_construct_map() -> pd.DataFrame:
    return read_csv_safe(CONSTRUCT_MAP)


@st.cache_data(ttl=600)
def load_triangulation_matrix() -> pd.DataFrame:
    return read_csv_safe(TRIANGULATION_MATRIX)


@st.cache_data(ttl=600)
def load_recommendation_rules() -> pd.DataFrame:
    return read_csv_safe(RECOMMENDATION_RULES)


