from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "outputs" / "runs"
DATA_SENTIMENT = ROOT / "data" / "processed" / "social_sentiment.csv"
DATA_SURVEY = ROOT / "data" / "processed" / "encuestas" / "model_ready.csv"

CONFIDENCE_LABEL = "Nivel de Confianza"
SENTIMENT_ORDER = ["negative", "neutral", "positive"]
CONFIDENCE_MAP = {1: "Baja", 2: "Media", 3: "Alta"}
PREFERRED_MODELS = ["svm_rbf", "random_forest", "voting_ensemble", "hist_gradient_boosting", "log_reg"]
NO_DATA_LABEL = "Sin dato"
AUTOMATION_LABEL = "Percepción"
REGULATION_LABEL = "Respuesta"
F1_LABEL = "F1 ponderado"
TRIANGULATION_DIMENSION = "Dimensión"
TRIANGULATION_SCRAPING = "Evidencia en scraping"
TRIANGULATION_SURVEY = "Evidencia en encuestas"
TRIANGULATION_READING = "Lectura integrada"


st.set_page_config(
    page_title="Plataforma de Resultados - Tesis IA Campañas",
    page_icon="https://aka-cdn.uce.edu.ec/ares/perseo/common/images/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2rem;
        }
        .hero-box {
            background: linear-gradient(135deg, #F2F7FA 0%, #FFFFFF 100%);
            border: 1px solid #0076BD;
            padding: 1.2rem 1.4rem;
            border-radius: 18px;
            margin-bottom: 1rem;
        }
        .section-note {
            background: #F7FAFC;
            border-left: 5px solid #0076BD;
            padding: 0.85rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    if not path or not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def latest_run_dir() -> Path | None:
    runs = sorted(RUNS_DIR.glob("run_*"))
    return runs[-1] if runs else None


def latest_file(folder: Path, pattern: str) -> Path | None:
    files = sorted(folder.glob(pattern))
    return files[-1] if files else None


def safe_to_datetime(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series.copy(), errors="coerce")
    from_epoch = pd.to_datetime(numeric, errors="coerce", unit="s")
    from_text = pd.to_datetime(series, errors="coerce")
    return pd.to_datetime(from_epoch.fillna(from_text), errors="coerce")


def normalize_sentiment_labels(df: pd.DataFrame) -> pd.DataFrame:
    if "sentiment_label" not in df.columns:
        return df
    out = df.copy()
    out["sentiment_label"] = out["sentiment_label"].astype(str).str.strip().str.lower()
    return out


def find_column(df: pd.DataFrame, required_terms: list[str]) -> str | None:
    normalized = {col: col.lower() for col in df.columns}
    for original, lowered in normalized.items():
        if all(term.lower() in lowered for term in required_terms):
            return original
    return None


def to_three_class_target(value: float) -> float:
    if pd.isna(value):
        return value
    if value <= 2:
        return 1
    if value == 3:
        return 2
    return 3


def confidence_distribution(survey_df: pd.DataFrame) -> pd.DataFrame:
    if survey_df.empty:
        return pd.DataFrame(columns=[CONFIDENCE_LABEL, "count", "share"])

    if "confianza_3" in survey_df.columns:
        series = pd.to_numeric(survey_df["confianza_3"], errors="coerce")
    else:
        rounded = pd.to_numeric(survey_df.get("confianza_idx_round"), errors="coerce")
        series = rounded.map(to_three_class_target)

    dist = (
        series.dropna()
        .astype(int)
        .map(CONFIDENCE_MAP)
        .value_counts()
        .reindex(["Baja", "Media", "Alta"], fill_value=0)
        .rename_axis(CONFIDENCE_LABEL)
        .reset_index(name="count")
    )
    total = dist["count"].sum()
    dist["share"] = dist["count"].div(total).fillna(0)
    return dist


def social_sentiment_distribution(sentiment_df: pd.DataFrame) -> pd.DataFrame:
    if sentiment_df.empty:
        return pd.DataFrame(columns=["sentiment_label", "count", "share"])
    dist = (
        sentiment_df["sentiment_label"]
        .value_counts()
        .reindex(SENTIMENT_ORDER, fill_value=0)
        .rename_axis("sentiment_label")
        .reset_index(name="count")
    )
    total = dist["count"].sum()
    dist["share"] = dist["count"].div(total).fillna(0)
    return dist


def response_distribution(survey_df: pd.DataFrame, terms: list[str], label: str) -> pd.DataFrame:
    column = find_column(survey_df, terms)
    if not column:
        return pd.DataFrame(columns=[label, "count", "share"])
    dist = survey_df[column].fillna(NO_DATA_LABEL).value_counts().reset_index()
    dist.columns = [label, "count"]
    total = dist["count"].sum()
    dist["share"] = dist["count"].div(total).fillna(0)
    return dist


def perception_score_table(survey_df: pd.DataFrame) -> pd.DataFrame:
    mappings = {
        "Manipulación percibida": ["partidos pueden manipular", "_num"],
        "Bots reducen confianza": ["bots o cuentas falsas", "_num"],
        "Deepfakes generan desconfianza": ["deepfakes", "_num"],
        "Regulación de IA": ["debería estar regulado", "_num"],
        "IA mejora transparencia": ["mejorar la transparencia", "_num"],
    }
    rows = []
    for label, terms in mappings.items():
        column = find_column(survey_df, terms)
        if not column:
            continue
        score = pd.to_numeric(survey_df[column], errors="coerce").mean()
        rows.append({"dimension": label, "score": score})
    return pd.DataFrame(rows)


def share_for_value(df: pd.DataFrame, key_col: str, value: str) -> float:
    if df.empty or key_col not in df.columns or "share" not in df.columns:
        return 0.0
    row = df[df[key_col] == value]
    return float(row["share"].iloc[0]) if not row.empty else 0.0


def describe_top_category(df: pd.DataFrame, key_col: str) -> str:
    if df.empty or key_col not in df.columns:
        return "No se encontraron datos suficientes para esta dimensión."
    top = df.sort_values("count", ascending=False).iloc[0]
    return f"La categoría dominante es '{top[key_col]}' con {top['share']:.1%} de las respuestas."


def build_triangulation_table(
    sentiment_dist: pd.DataFrame,
    confidence_dist: pd.DataFrame,
    automation_dist: pd.DataFrame,
    regulation_dist: pd.DataFrame,
) -> pd.DataFrame:
    negative_share = share_for_value(sentiment_dist, "sentiment_label", "negative")
    positive_share = share_for_value(sentiment_dist, "sentiment_label", "positive")
    low_conf_share = share_for_value(confidence_dist, CONFIDENCE_LABEL, "Baja")
    high_conf_share = share_for_value(confidence_dist, CONFIDENCE_LABEL, "Alta")
    return pd.DataFrame(
        [
            {
                TRIANGULATION_DIMENSION: "Clima informativo digital",
                TRIANGULATION_SCRAPING: f"{negative_share:.1%} del contenido analizado presenta sentimiento negativo.",
                TRIANGULATION_SURVEY: f"{low_conf_share:.1%} de la muestra se ubica en baja confianza electoral.",
                TRIANGULATION_READING: "Existe correspondencia descriptiva entre un entorno digital crítico y una ciudadanía más desconfiada.",
            },
            {
                TRIANGULATION_DIMENSION: "Señales positivas y confianza alta",
                TRIANGULATION_SCRAPING: f"{positive_share:.1%} del contenido analizado presenta sentimiento positivo.",
                TRIANGULATION_SURVEY: f"{high_conf_share:.1%} de la muestra se ubica en alta confianza electoral.",
                TRIANGULATION_READING: "La comparación sirve como contraste descriptivo, no como equivalencia causal entre sentimiento y confianza.",
            },
            {
                TRIANGULATION_DIMENSION: "Automatización y manipulación",
                TRIANGULATION_SCRAPING: "El corpus social recoge actividad política digital en múltiples plataformas y usuarios.",
                TRIANGULATION_SURVEY: describe_top_category(automation_dist, AUTOMATION_LABEL),
                TRIANGULATION_READING: "Las percepciones de automatización pueden interpretarse junto con el volumen y tono del ecosistema digital observado.",
            },
            {
                TRIANGULATION_DIMENSION: "Regulación y respuesta pública",
                TRIANGULATION_SCRAPING: "El debate digital permite contextualizar riesgos y tensiones del uso político de IA.",
                TRIANGULATION_SURVEY: describe_top_category(regulation_dist, REGULATION_LABEL),
                TRIANGULATION_READING: "La demanda de regulación puede leerse como respuesta social frente a un entorno digital intensificado.",
            },
        ]
    )


@st.cache_data
def load_run_artifacts(run_dir: Path | None) -> dict[str, object]:
    if run_dir is None:
        return {}
    tables_dir = run_dir / "tables"
    figures_dir = run_dir / "figures"
    metrics_path = latest_file(tables_dir, "metrics_run_*.csv")
    compare_path = tables_dir / "metrics_compare_all_models.csv"
    importance_path = latest_file(tables_dir, "rf_feature_importance_*.csv")
    return {
        "metrics": load_csv(metrics_path),
        "compare": load_csv(compare_path),
        "importance": load_csv(importance_path),
        "figures_dir": figures_dir,
    }


def humanize_model_name(name: str) -> str:
    labels = {
        "svm_rbf": "SVM-RBF",
        "random_forest": "Random Forest",
        "voting_ensemble": "Voting Ensemble",
        "hist_gradient_boosting": "HistGradientBoosting",
        "log_reg": "Regresión Logística",
        "ordinal_logit": "Regresión Logística Ordinal",
        "baseline_majority": "Baseline Mayoría",
        "baseline_stratified": "Baseline Estratificado",
    }
    return labels.get(name, name)


def model_leaderboard(compare_df: pd.DataFrame, metrics_df: pd.DataFrame) -> pd.DataFrame:
    if not compare_df.empty:
        out = compare_df.copy()
        out["model_label"] = out["model"].map(humanize_model_name)
        return out.sort_values(["f1_weighted", "kappa_qw", "accuracy"], ascending=False)
    if metrics_df.empty:
        return pd.DataFrame()
    out = metrics_df.copy()
    out["model_label"] = out["model"].map(humanize_model_name)
    out["accuracy"] = out["accuracy_mean"]
    out["f1_weighted"] = out["f1_weighted_mean"]
    out["auc_ovr"] = out["auc_ovr_mean"]
    out["kappa_qw"] = out["kappa_qw_mean"]
    out["time_seconds"] = out["time_seconds_mean"]
    return out.sort_values(["f1_weighted", "kappa_qw", "accuracy"], ascending=False)


def best_model_row(leaderboard: pd.DataFrame) -> pd.Series | None:
    return None if leaderboard.empty else leaderboard.iloc[0]


def render_model_figure(figures_dir: Path, model_name: str) -> None:
    image_path = latest_file(figures_dir, f"cm_{model_name}_*_norm.png")
    if image_path:
        st.image(str(image_path), caption=f"Matriz de confusión normalizada - {humanize_model_name(model_name)}")


inject_css()

run_dir = latest_run_dir()
sentiment_df = normalize_sentiment_labels(load_csv(DATA_SENTIMENT))
survey_df = load_csv(DATA_SURVEY)
artifacts = load_run_artifacts(run_dir)

if sentiment_df.empty:
    st.warning("No se encontró social_sentiment.csv. Ejecuta primero el flujo de scraping y análisis de sentimiento.")
    st.stop()

if survey_df.empty:
    st.warning("No se encontró model_ready.csv en data/processed/encuestas.")
    st.stop()

sentiment_df["date_parsed"] = safe_to_datetime(sentiment_df["date"])

st.logo("https://aka-cdn.uce.edu.ec/ares/perseo/common/images/logo.png")

st.markdown(
    """
    <div class="hero-box" style="display: flex; align-items: center; gap: 20px;">
        <img src="https://aka-cdn.uce.edu.ec/ares/perseo/common/images/logo.png" style="height: 80px;" alt="Logo UCE">
        <div>
            <h2 style="margin:0; color:#0076BD;">Universidad Central del Ecuador</h2>
            <h3 style="margin:0; color:#C00E19; font-size: 1.2rem;">Facultad de Comunicación Social</h3>
            <p style="margin:0.45rem 0 0 0; color:#333333; font-weight: 500;">
                Plataforma Web de Resultados: IA en Campañas Electorales
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"Run analítico cargado: {run_dir.name if run_dir else 'No disponible'}")

st.sidebar.header("Filtros del ecosistema digital")
platforms = sorted(sentiment_df["platform"].dropna().unique().tolist())
sentiments = [value for value in SENTIMENT_ORDER if value in sentiment_df["sentiment_label"].unique().tolist()]
selected_platforms = st.sidebar.multiselect("Plataformas", platforms, default=platforms)
selected_sentiments = st.sidebar.multiselect("Sentimientos", sentiments, default=sentiments)

date_series = sentiment_df["date_parsed"].dropna()
selected_range = None
if not date_series.empty:
    selected_range = st.sidebar.date_input(
        "Rango de fechas",
        value=(date_series.min().date(), date_series.max().date()),
        min_value=date_series.min().date(),
        max_value=date_series.max().date(),
    )

filtered_social = sentiment_df[
    sentiment_df["platform"].isin(selected_platforms)
    & sentiment_df["sentiment_label"].isin(selected_sentiments)
].copy()

if selected_range:
    start_date, end_date = selected_range
    filtered_social = filtered_social[
        (filtered_social["date_parsed"].dt.date >= start_date)
        & (filtered_social["date_parsed"].dt.date <= end_date)
    ]

sentiment_dist = social_sentiment_distribution(filtered_social)
confidence_dist = confidence_distribution(survey_df)
automation_dist = response_distribution(survey_df, ["percibe_automatizacion"], AUTOMATION_LABEL)
regulation_dist = response_distribution(survey_df, ["debería regularse"], REGULATION_LABEL)
perception_scores = perception_score_table(survey_df)
leaderboard = model_leaderboard(artifacts.get("compare", pd.DataFrame()), artifacts.get("metrics", pd.DataFrame()))
best_model = best_model_row(leaderboard)

negative_share = share_for_value(sentiment_dist, "sentiment_label", "negative")
low_conf_share = share_for_value(confidence_dist, CONFIDENCE_LABEL, "Baja")

metric_cols = st.columns(6)
metric_cols[0].metric("Posts analizados", f"{len(filtered_social):,}")
metric_cols[1].metric("Plataformas", f"{filtered_social['platform'].nunique()}")
metric_cols[2].metric("Usuarios observados", f"{filtered_social['user'].nunique()}")
metric_cols[3].metric("Encuestas válidas", f"{len(survey_df):,}")
metric_cols[4].metric("Sentimiento negativo", f"{negative_share:.1%}")
metric_cols[5].metric("Confianza baja", f"{low_conf_share:.1%}")

overview_tab, digital_tab, survey_tab, compare_tab, models_tab, explorer_tab = st.tabs(
    [
        "Resumen ejecutivo",
        "Panorama digital",
        "Percepción ciudadana",
        "Triangulación",
        "Modelado predictivo",
        "Explorador de datos",
    ]
)

with overview_tab:
    st.markdown(
        '<div class="section-note">Esta vista resume el entorno digital observado, la respuesta ciudadana y el comportamiento del modelo predictivo principal.</div>',
        unsafe_allow_html=True,
    )
    col_a, col_b = st.columns([1.15, 1])
    with col_a:
        fig_sentiment = px.bar(
            sentiment_dist,
            x="sentiment_label",
            y="count",
            color="sentiment_label",
            category_orders={"sentiment_label": SENTIMENT_ORDER},
            color_discrete_map={"negative": "#d1495b", "neutral": "#9aa5b1", "positive": "#2d936c"},
            text_auto=True,
            title="Distribución de sentimiento en scraping social",
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
    with col_b:
        fig_confidence = px.bar(
            confidence_dist,
            x=CONFIDENCE_LABEL,
            y="count",
            color=CONFIDENCE_LABEL,
            category_orders={CONFIDENCE_LABEL: ["Baja", "Media", "Alta"]},
            color_discrete_map={"Baja": "#d1495b", "Media": "#e9b44c", "Alta": "#2d936c"},
            text_auto=True,
            title="Distribución de confianza electoral (3 clases)",
        )
        st.plotly_chart(fig_confidence, use_container_width=True)

    st.subheader("Lectura integrada")
    st.write(
        f"El entorno digital analizado presenta {negative_share:.1%} de sentimiento negativo, mientras que la encuesta reporta {low_conf_share:.1%} de baja confianza electoral. Esta relación debe leerse como triangulación descriptiva entre evidencia observada y percepción ciudadana, no como causalidad directa."
    )
    if best_model is not None:
        st.subheader("Mejor modelo del pipeline")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Modelo", humanize_model_name(str(best_model["model"])))
        c2.metric("Accuracy", f"{float(best_model['accuracy']):.3f}")
        c3.metric("F1 ponderado", f"{float(best_model['f1_weighted']):.3f}")
        c4.metric("AUC", f"{float(best_model['auc_ovr']):.3f}")

with digital_tab:
    st.subheader("Ecosistema digital observado por scraping")
    c1, c2 = st.columns(2)
    with c1:
        platform_dist = (
            filtered_social.groupby(["platform", "sentiment_label"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
        )
        fig_platform = px.bar(
            platform_dist,
            x="platform",
            y="count",
            color="sentiment_label",
            barmode="group",
            text_auto=True,
            title="Sentimiento por plataforma",
            color_discrete_map={"negative": "#d1495b", "neutral": "#9aa5b1", "positive": "#2d936c"},
        )
        st.plotly_chart(fig_platform, use_container_width=True)
    with c2:
        if filtered_social["date_parsed"].notna().any():
            weekly = (
                filtered_social.dropna(subset=["date_parsed"])
                .groupby(pd.Grouper(key="date_parsed", freq="W"))
                .size()
                .reset_index(name="count")
            )
            fig_weekly = px.line(
                weekly,
                x="date_parsed",
                y="count",
                markers=True,
                title="Evolución temporal de publicaciones",
            )
            st.plotly_chart(fig_weekly, use_container_width=True)
        else:
            st.info("No hay fechas válidas para construir la serie temporal.")

    top_users = (
        filtered_social[["user"]]
        .fillna("(sin usuario)")
        .groupby("user", as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .nlargest(15, "count")
    )
    fig_users = px.bar(
        top_users,
        x="count",
        y="user",
        orientation="h",
        text_auto=True,
        title="Top 15 usuarios por volumen de publicaciones",
    )
    st.plotly_chart(fig_users, use_container_width=True)

with survey_tab:
    st.subheader("Percepción ciudadana levantada por encuesta")
    c1, c2 = st.columns(2)
    with c1:
        gender_dist = survey_df["genero"].fillna(NO_DATA_LABEL).value_counts().reset_index()
        gender_dist.columns = ["Género", "count"]
        fig_gender = px.pie(gender_dist, names="Género", values="count", title="Distribución por género")
        st.plotly_chart(fig_gender, use_container_width=True)

        age_dist = survey_df["edad"].fillna(NO_DATA_LABEL).value_counts().reset_index()
        age_dist.columns = ["Edad", "count"]
        fig_age = px.bar(age_dist, x="Edad", y="count", text_auto=True, title="Distribución por edad")
        st.plotly_chart(fig_age, use_container_width=True)
    with c2:
        fig_conf_survey = px.bar(
            confidence_dist,
            x=CONFIDENCE_LABEL,
            y="count",
            color=CONFIDENCE_LABEL,
            category_orders={CONFIDENCE_LABEL: ["Baja", "Media", "Alta"]},
            text_auto=True,
            title="Confianza electoral recodificada a 3 clases",
        )
        st.plotly_chart(fig_conf_survey, use_container_width=True)
        if not automation_dist.empty:
            fig_automation = px.bar(
                automation_dist,
                x=AUTOMATION_LABEL,
                y="count",
                text_auto=True,
                title="Percepción de automatización en campañas",
            )
            st.plotly_chart(fig_automation, use_container_width=True)

    st.subheader("Promedio de percepciones clave sobre IA")
    if not perception_scores.empty:
        fig_scores = px.bar(
            perception_scores.sort_values("score"),
            x="score",
            y="dimension",
            orientation="h",
            text_auto=".2f",
            title="Promedio Likert de afirmaciones centrales",
            range_x=[1, 5],
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    else:
        st.info("No se encontraron columnas numéricas de percepción para resumir.")

with compare_tab:
    st.subheader("Triangulación entre scraping y encuestas")
    st.markdown(
        '<div class="section-note">La consolidación se realiza a nivel interpretativo. El scraping representa el entorno digital observado y la encuesta recoge la percepción ciudadana declarada.</div>',
        unsafe_allow_html=True,
    )
    compare_df = pd.DataFrame(
        {
            "Indicador": ["Sentimiento negativo en scraping", "Confianza baja en encuestas", "Sentimiento positivo en scraping", "Confianza alta en encuestas"],
            "Porcentaje": [
                share_for_value(sentiment_dist, "sentiment_label", "negative"),
                share_for_value(confidence_dist, CONFIDENCE_LABEL, "Baja"),
                share_for_value(sentiment_dist, "sentiment_label", "positive"),
                share_for_value(confidence_dist, CONFIDENCE_LABEL, "Alta"),
            ],
            "Fuente": ["Scraping", "Encuesta", "Scraping", "Encuesta"],
        }
    )
    col_left, col_right = st.columns(2)
    with col_left:
        fig_compare = px.bar(
            compare_df,
            x="Indicador",
            y="Porcentaje",
            color="Fuente",
            barmode="group",
            text_auto=".1%",
            title="Contraste descriptivo entre ecosistema digital y confianza electoral",
        )
        fig_compare.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_compare, use_container_width=True)
    with col_right:
        st.markdown("### Hallazgos integrados")
        st.write(f"- {describe_top_category(automation_dist, AUTOMATION_LABEL)}")
        st.write(f"- {describe_top_category(regulation_dist, REGULATION_LABEL)}")
        st.write("- La coincidencia entre mayor negatividad del entorno digital y un bloque importante de baja confianza fortalece la narrativa de escepticismo político-digital.")
        st.write("- La lectura correcta para tesis es de triangulación metodológica, no de equivalencia causal entre scraping y encuesta.")

    st.subheader("Matriz de triangulación")
    st.dataframe(
        build_triangulation_table(sentiment_dist, confidence_dist, automation_dist, regulation_dist),
        use_container_width=True,
        hide_index=True,
    )

with models_tab:
    st.subheader("Resultados del modelado predictivo")
    if leaderboard.empty:
        st.warning("No se encontraron métricas del modelado en el último run.")
    else:
        model_metrics = leaderboard[leaderboard["model"].isin(PREFERRED_MODELS)].copy()
        fig_models = px.bar(
            model_metrics,
            x="model_label",
            y=["accuracy", "f1_weighted", "auc_ovr"],
            barmode="group",
            title="Comparación de métricas por modelo",
        )
        st.plotly_chart(fig_models, use_container_width=True)

        st.dataframe(
            model_metrics[["model_label", "accuracy", "f1_weighted", "auc_ovr", "kappa_qw", "time_seconds"]]
            .rename(columns={
                "model_label": "Modelo",
                "accuracy": "Accuracy",
                "f1_weighted": F1_LABEL,
                "auc_ovr": "AUC",
                "kappa_qw": "QWK",
                "time_seconds": "Tiempo (s)",
            }),
            use_container_width=True,
            hide_index=True,
        )

        if best_model is not None:
            st.markdown("### Mejor modelo")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Modelo", humanize_model_name(str(best_model["model"])))
            m2.metric("Accuracy", f"{float(best_model['accuracy']):.3f}")
            m3.metric(F1_LABEL, f"{float(best_model['f1_weighted']):.3f}")
            m4.metric("AUC", f"{float(best_model['auc_ovr']):.3f}")

        importance_df = artifacts.get("importance", pd.DataFrame())
        if isinstance(importance_df, pd.DataFrame) and not importance_df.empty:
            st.markdown("### Variables más influyentes en Random Forest")
            top_importance = importance_df.head(15).copy()
            top_importance["feature"] = top_importance["feature"].astype(str).str.slice(0, 85)
            fig_importance = px.bar(
                top_importance.sort_values("importance"),
                x="importance",
                y="feature",
                orientation="h",
                text_auto=".3f",
                title="Top variables por importancia",
            )
            st.plotly_chart(fig_importance, use_container_width=True)

        available_models = [
            model for model in PREFERRED_MODELS if latest_file(artifacts.get("figures_dir"), f"cm_{model}_*_norm.png")
        ]
        if available_models:
            selected_model = st.selectbox(
                "Selecciona un modelo para visualizar su matriz de confusión",
                options=available_models,
                format_func=humanize_model_name,
            )
            render_model_figure(artifacts.get("figures_dir"), selected_model)

with explorer_tab:
    st.subheader("Explorador de datos")
    source = st.radio("Selecciona la fuente", ["Scraping social", "Encuestas"], horizontal=True)
    if source == "Scraping social":
        st.dataframe(filtered_social, use_container_width=True, height=520)
    else:
        st.dataframe(survey_df, use_container_width=True, height=520)
