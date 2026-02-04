from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px


ROOT = Path(__file__).resolve().parents[1]
DATA_SENTIMENT = ROOT / "data" / "processed" / "social_sentiment.csv"
DATA_SURVEY = ROOT / "data" / "processed" / "model_ready.csv"
KEYWORDS_REPORT = ROOT / "outputs" / "latest" / "tables" / "resumen_sentimiento_keywords.md"
METRICS_DIR = ROOT / "outputs" / "latest" / "tables"
CONFIDENCE_LEVEL = "Nivel de Confianza"


st.set_page_config(
    page_title="Dashboard - Tesis IA Campañas",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_sentiment(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


@st.cache_data
def load_survey(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


@st.cache_data
def load_latest_metrics(metrics_dir: Path) -> pd.DataFrame:
    if not metrics_dir.exists():
        return pd.DataFrame()
    files = sorted(metrics_dir.glob("metrics_run_*.csv"))
    if not files:
        return pd.DataFrame()
    return pd.read_csv(files[-1], encoding="utf-8-sig")


@st.cache_data
def load_latest_seed_metrics(metrics_dir: Path) -> pd.DataFrame:
    if not metrics_dir.exists():
        return pd.DataFrame()
    files = sorted(metrics_dir.glob("metrics_by_seed_*.csv"))
    if not files:
        return pd.DataFrame()
    return pd.read_csv(files[-1], encoding="utf-8-sig")


def safe_to_datetime(series: pd.Series) -> pd.Series:
    series = series.copy()
    # Separar valores numéricos (epoch) de strings para evitar mezclas de dtype
    numeric = pd.to_numeric(series, errors="coerce")
    from_epoch = pd.to_datetime(numeric, errors="coerce", unit="s")
    from_text = pd.to_datetime(series, errors="coerce")
    combined = from_epoch.fillna(from_text)
    return pd.to_datetime(combined, errors="coerce")


st.title("📊 Plataforma de Resultados - Tesis IA Campañas")
st.caption("Resultados exploratorios de encuestas y redes sociales en contexto electoral")

sentiment_df = load_sentiment(DATA_SENTIMENT)

if sentiment_df.empty:
    st.warning("No hay datos en social_sentiment.csv. Ejecuta la limpieza y el análisis de sentimiento.")
    st.stop()

# Sidebar filtros
st.sidebar.header("Filtros")
platforms = sorted(sentiment_df["platform"].dropna().unique().tolist())
platform_sel = st.sidebar.multiselect("Plataforma", platforms, default=platforms)

sentiments = sorted(sentiment_df["sentiment_label"].dropna().unique().tolist())
sentiment_sel = st.sidebar.multiselect("Sentimiento", sentiments, default=sentiments)

sentiment_df["date_parsed"] = safe_to_datetime(sentiment_df["date"])

date_series = sentiment_df["date_parsed"].dropna()
min_date = date_series.min() if not date_series.empty else pd.NaT
max_date = date_series.max() if not date_series.empty else pd.NaT

if pd.notna(min_date) and pd.notna(max_date):
    date_range = st.sidebar.date_input(
        "Rango de fechas",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )
else:
    date_range = None

filtered = sentiment_df[
    sentiment_df["platform"].isin(platform_sel)
    & sentiment_df["sentiment_label"].isin(sentiment_sel)
]

if date_range:
    start, end = date_range
    filtered = filtered[
        (filtered["date_parsed"].dt.date >= start)
        & (filtered["date_parsed"].dt.date <= end)
    ]


col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros", f"{len(filtered):,}")
col2.metric("Plataformas", f"{filtered['platform'].nunique()}")
col3.metric("Usuarios", f"{filtered['user'].nunique()}")
col4.metric("Fuentes", f"{filtered['source_url'].nunique()}")

st.divider()

# Tabs principales
overview_tab, sentiment_tab, survey_tab, models_tab, data_tab = st.tabs(
    ["Resumen RRSS", "Sentimiento", "Encuestas", "Modelos", "Datos RRSS"]
)

with overview_tab:
    st.subheader("Distribución general")

    dist = (
        filtered.groupby("sentiment_label", as_index=False)
        .size()
        .rename(columns={"sentiment_label": "sentiment", "size": "count"})
    )

    fig = px.bar(
        dist,
        x="sentiment",
        y="count",
        color="sentiment",
        text_auto=True,
        title="Distribución de sentimiento",
    )
    st.plotly_chart(fig, width="stretch")

    platform_dist = (
        filtered.groupby(["platform", "sentiment_label"], as_index=False)
        .size()
        .rename(columns={"sentiment_label": "sentiment", "size": "count"})
    )

    fig_platform = px.bar(
        platform_dist,
        x="platform",
        y="count",
        color="sentiment",
        barmode="group",
        text_auto=True,
        title="Sentimiento por plataforma",
    )
    st.plotly_chart(fig_platform, width="stretch")

    if KEYWORDS_REPORT.exists():
        st.subheader("Resumen por palabras clave")
        st.markdown(KEYWORDS_REPORT.read_text(encoding="utf-8"))


with sentiment_tab:
    st.subheader("Tendencia temporal")
    if filtered["date_parsed"].notna().any():
        time_df = (
            filtered.dropna(subset=["date_parsed"])
            .groupby(pd.Grouper(key="date_parsed", freq="W"))
            .size()
            .reset_index(name="count")
        )
        fig_time = px.line(
            time_df,
            x="date_parsed",
            y="count",
            markers=True,
            title="Publicaciones por semana",
        )
        st.plotly_chart(fig_time, width="stretch")
    else:
        st.info("No hay fechas válidas para graficar la tendencia temporal.")

    st.subheader("Top usuarios por volumen")
    top_users = (
        filtered[["user"]].fillna("(sin usuario)")
        .groupby("user", as_index=False).size()
        .nlargest(15, "size")
        .rename(columns={"size": "count"})
    )
    fig_users = px.bar(
        top_users,
        x="count",
        y="user",
        orientation="h",
        text_auto=True,
        title="Top 15 usuarios",
    )
    st.plotly_chart(fig_users, width="stretch")


with survey_tab:
    st.subheader("Análisis de Encuestas")
    survey_df = load_survey(DATA_SURVEY)

    if survey_df.empty:
        st.warning("No se encontró model_ready.csv en data/processed.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            # Distribución de Género
            gender_df = survey_df["genero"].value_counts().reset_index()
            gender_df.columns = ["Género", "Cantidad"]
            fig_gen = px.pie(gender_df, names="Género", values="Cantidad", title="Distribución por Género")
            st.plotly_chart(fig_gen, width="stretch")

            # Percepción de IA
            ia_aware = survey_df["conoce_ia"].value_counts().reset_index()
            ia_aware.columns = ["Conoce IA", "Cantidad"]
            fig_ia = px.bar(ia_aware, x="Conoce IA", y="Cantidad", title="¿Conoce sobre Inteligencia Artificial?")
            st.plotly_chart(fig_ia, width="stretch")

        with c2:
            # Distribución de Edad
            age_df = survey_df["edad"].value_counts().reset_index()
            age_df.columns = ["Edad", "Cantidad"]
            fig_age = px.bar(age_df, x="Edad", y="Cantidad", title="Distribución por Edad")
            st.plotly_chart(fig_age, width="stretch")

            # Confianza Electoral
            conf_df = survey_df["confianza_idx_round"].value_counts().reset_index()
            conf_df.columns = [CONFIDENCE_LEVEL, "Cantidad"]
            conf_df = conf_df.sort_values(CONFIDENCE_LEVEL)
            fig_conf = px.bar(conf_df, x=CONFIDENCE_LEVEL, y="Cantidad",
            title=f"{CONFIDENCE_LEVEL} en el Proceso Electoral (1-5)")
            st.plotly_chart(fig_conf, width="stretch")

        st.subheader("Resumen de Percepciones sobre IA")
        # Mostrar algunas columnas de percepción clave si existen
        perc_cols = [c for c in survey_df.columns if "Percepción" in c]
        if perc_cols:
            selected_perc = st.selectbox("Seleccionar pregunta de percepción:", perc_cols)
            perc_data = survey_df[selected_perc].value_counts().reset_index()
            perc_data.columns = ["Respuesta", "Cantidad"]
            fig_perc = px.bar(perc_data, x="Respuesta", y="Cantidad", title=selected_perc)
            st.plotly_chart(fig_perc, width="stretch")


with models_tab:
    st.subheader("Comparación de modelos predictivos")

    metrics_df = load_latest_metrics(METRICS_DIR)
    seed_df = load_latest_seed_metrics(METRICS_DIR)

    if metrics_df.empty:
        st.warning("No se encontró metrics_run_*.csv en outputs/latest/tables.")
    else:
        st.dataframe(metrics_df, width="stretch")

    if not seed_df.empty:
        st.subheader("Métricas por semilla")
        st.dataframe(seed_df, width="stretch")


with data_tab:
    st.subheader("Datos filtrados")
    st.dataframe(filtered, width="stretch", height=520)
