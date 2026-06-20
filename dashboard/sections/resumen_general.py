# dashboard/sections/resumen_general.py
import pandas as pd
import streamlit as st
import plotly.express as px


from textwrap import dedent

from dashboard.components import (
    topbar,
    kpi_card,
    method_card,
)


from dashboard.common import (
    PLOTLY_CONFIG,
    find_first_existing_column,
    empty_state,
    make_category_distribution,
    make_likert_distribution,
    horizontal_bar_chart,
    donut_chart,
    render_card_header,
)

CONFIDENCE_LABELS = {
    1: "Muy baja confianza",
    2: "Baja confianza",
    3: "Confianza moderada",
    4: "Alta confianza",
    5: "Muy alta confianza",
}


LIKERT_LABELS = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Ni de acuerdo ni en desacuerdo",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}


REGULATION_LABELS = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Ni de acuerdo ni en desacuerdo",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}


PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}

LIKERT_COLORS = {
    "Totalmente en desacuerdo": "#1D4ED8",
    "En desacuerdo": "#93C5FD",
    "Ni de acuerdo ni en desacuerdo": "#CBD5E1",
    "De acuerdo": "#99F6E4",
    "Totalmente de acuerdo": "#14B8A6",
}

CONFIDENCE_COLORS = {
    "Muy baja confianza": "#F97316",
    "Baja confianza": "#FDBA74",
    "Confianza moderada": "#CBD5E1",
    "Alta confianza": "#99F6E4",
    "Muy alta confianza": "#14B8A6",
}

SCALE_COLORS = {
    **LIKERT_COLORS,
    **CONFIDENCE_COLORS,
}

def render_html(markup: str) -> None:
    st.markdown(
        "\n".join(
            line.strip()
            for line in dedent(markup).splitlines()
            if line.strip()
        ),
        unsafe_allow_html=True,
    )

def pretty_model_name(name: str) -> str:
    if not name or name == "No disponible":
        return "No disponible"

    mapping = {
        "random_forest": "Random Forest",
        "log_reg": "Regresión logística",
        "svm_rbf": "SVM-RBF",
        "hist_gradient_boosting": "Gradient Boosting",
        "voting_ensemble": "Voting Ensemble",
        "baseline_majority": "Baseline mayoría",
        "baseline_stratified": "Baseline estratificado",
    }

    return mapping.get(str(name), str(name).replace("_", " ").title())


def get_best_model(metrics_df: pd.DataFrame):
    if metrics_df is None or metrics_df.empty:
        return "No disponible", None

    def find_col(candidates):
        normalized = {str(c).lower().strip(): c for c in metrics_df.columns}

        for candidate in candidates:
            key = candidate.lower().strip()
            if key in normalized:
                return normalized[key]

        for col in metrics_df.columns:
            col_l = str(col).lower().strip()
            for candidate in candidates:
                if candidate.lower().strip() in col_l:
                    return col

        return None

    model_col = find_col([
        "model",
        "modelo",
        "model_name",
        "nombre_modelo",
        "algoritmo",
    ])

    metric_col = find_col([
        "f1_weighted_mean",
        "f1_weighted",
        "f1-w",
        "f1_w",
        "f1",
        "accuracy_mean",
        "accuracy",
        "exactitud",
        "exactitud promedio",
    ])

    selected_col = find_col([
        "selected",
        "seleccionado",
        "modelo_seleccionado",
    ])

    if model_col is None:
        return "No disponible", None

    df = metrics_df.copy()

    # 1. Si existe una columna de seleccionado, priorizarla
    if selected_col is not None:
        selected_mask = (
            df[selected_col]
            .astype(str)
            .str.lower()
            .str.contains("seleccionado|selected|true|1|sí|si", regex=True, na=False)
        )

        if selected_mask.any():
            best = df[selected_mask].iloc[0]
            score = None

            if metric_col is not None:
                score = pd.to_numeric(best[metric_col], errors="coerce")
                score = None if pd.isna(score) else float(score)

            return pretty_model_name(str(best[model_col])), score

    # 2. Si existe métrica, escoger el mejor por esa métrica
    if metric_col is not None:
        df["_metric_tmp"] = pd.to_numeric(df[metric_col], errors="coerce")

        if df["_metric_tmp"].notna().any():
            best = df.sort_values("_metric_tmp", ascending=False).iloc[0]
            return pretty_model_name(str(best[model_col])), float(best["_metric_tmp"])

    # 3. Fallback: si aparece Random Forest, usarlo
    rf_mask = (
        df[model_col]
        .astype(str)
        .str.lower()
        .str.contains("random_forest|random forest", regex=True, na=False)
    )

    if rf_mask.any():
        best = df[rf_mask].iloc[0]
        return "Random Forest", None

    # 4. Último fallback
    best = df.iloc[0]
    return pretty_model_name(str(best[model_col])), None    


def find_first_existing_column(df: pd.DataFrame, candidates: list[str]):
    """
    Busca una columna por coincidencia exacta o parcial.
    Sirve para tolerar nombres distintos en el CSV.
    """
    if df.empty:
        return None

    normalized = {c.lower().strip(): c for c in df.columns}

    for candidate in candidates:
        key = candidate.lower().strip()
        if key in normalized:
            return normalized[key]

    for col in df.columns:
        col_l = col.lower().strip()
        for candidate in candidates:
            if candidate.lower().strip() in col_l:
                return col

    return None


def make_distribution_from_scale(
    df: pd.DataFrame,
    col: str,
    labels: dict[int, str],
    order: list[str],
) -> pd.DataFrame:
    """
    Convierte una columna ordinal 1-5 en una distribución porcentual.
    Solo usa respuestas válidas entre 1 y 5.
    """
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=["Respuesta", "Cantidad", "Porcentaje"])

    numeric = pd.to_numeric(df[col], errors="coerce").round()

    temp = pd.DataFrame({"valor": numeric})
    temp = temp[temp["valor"].isin(labels.keys())].copy()

    if temp.empty:
        return pd.DataFrame(columns=["Respuesta", "Cantidad", "Porcentaje"])

    temp["Respuesta"] = temp["valor"].astype(int).map(labels)

    counts = (
        temp["Respuesta"]
        .value_counts()
        .reindex(order)
        .fillna(0)
        .astype(int)
    )

    total = counts.sum()

    if total == 0:
        return pd.DataFrame(columns=["Respuesta", "Cantidad", "Porcentaje"])

    out = pd.DataFrame(
        {
            "Respuesta": counts.index,
            "Cantidad": counts.values,
            "Porcentaje": (counts.values / total * 100).round(1),
        }
    )

    return out[out["Cantidad"] > 0].copy()


def make_stacked_bar(values: pd.DataFrame, title_y: str, height: int = 190):
    """
    Barra apilada compacta para escalas ordinales.
    """
    if values.empty or values["Porcentaje"].sum() <= 0:
        return None

    fig = px.bar(
        values,
        x="Porcentaje",
        y=[title_y] * len(values),
        color="Respuesta",
        orientation="h",
        text="Porcentaje",
        category_orders={"Respuesta": values["Respuesta"].tolist()},
        color_discrete_map=SCALE_COLORS,
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate="<b>%{customdata}</b><br>Porcentaje: %{x:.1f}%<extra></extra>",
        customdata=values["Respuesta"],
    )


    fig.update_layout(
        barmode="stack",
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        xaxis=dict(
            visible=False,
            range=[0, 100],
        ),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=4, b=52),
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.08,
            xanchor="left",
            x=0,
            font=dict(size=10),
        ),
    

    )

    return fig


def empty_state(message: str):
    st.markdown(
        f"""
        <div class="empty-state">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_resumen_general(
    survey_df: pd.DataFrame,
    news_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
):
    n_survey = len(survey_df) if not survey_df.empty else 0
    n_news = len(news_df) if not news_df.empty else 0

    n_cases = (
        news_df["case_id"].nunique()
        if not news_df.empty and "case_id" in news_df.columns
        else 0
    )

    n_domains = (
        news_df["domain"].nunique()
        if not news_df.empty and "domain" in news_df.columns
        else 0
    )

    best_model, best_score = get_best_model(metrics_df)

    # =========================================================
    # ENCABEZADO
    # =========================================================
    topbar(
        title="Resumen General",
        subtitle=(
            "Análisis de la percepción ciudadana sobre el uso de inteligencia artificial "
            "en campañas políticas digitales. Caso: elecciones presidenciales Ecuador 2025."
        ),
        pill_text=f"n = {n_survey:,} encuestas" if n_survey else "encuestas no cargadas",
    )

    st.markdown("## Resumen General del Estudio")
    st.markdown(
        """
        Esta plataforma presenta los resultados del trabajo de titulación sobre la percepción ciudadana
        frente al uso de inteligencia artificial en campañas políticas digitales. La encuesta constituye
        la fuente principal del análisis; los registros de redes y medios se incorporan como evidencia
        digital complementaria y exploratoria.
        """
    )

    # =========================================================
    # KPI CARDS
    # =========================================================
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi_card(
            "Encuestas válidas",
            f"{n_survey:,}",
            "Registros procesados de la muestra",
            "blue",
        )

    with c2:
        kpi_card(
            "Corpus analíticos",
            f"{n_cases:,}",
            "Casos o fuentes de evidencia digital agrupada",
            "purple",
        )

    with c3:
        kpi_card(
            "Registros digitales",
            f"{n_news:,}",
            "Registros de GDELT, medios o redes procesadas",
            "yellow",
        )

    with c4:
        kpi_card(
            "Dominios",
            f"{n_domains:,}",
            "Fuentes informativas únicas",
            "green",
        )

    with c5:
        score_label = f"{best_score:.3f}" if best_score is not None else "N/D"
        kpi_card(
            "Mejor modelo",
            best_model,
            f"F1 ponderado: {score_label}",
            "cyan",
        )

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # =========================================================
    # HIPÓTESIS + PERFIL
    # =========================================================
    left, right = st.columns([1, 1], gap="medium")

    with left:

        render_html(
            """
            <div class="custom-card">
                <div class="card-title">Hipótesis del estudio</div>

                <div class="hypothesis-grid">
                    <div class="hypothesis-box h1-box">
                        <div class="hypothesis-label">H1 · Exposición y confianza</div>
                        <div class="hypothesis-text">
                            A mayor exposición percibida a contenidos generados o potenciados por IA,
                            menor nivel de confianza electoral en la comunidad universitaria UCE.
                        </div>
                    </div>

                    <div class="hypothesis-box h2-box">
                        <div class="hypothesis-label">H2 · Verificación informativa</div>
                        <div class="hypothesis-text">
                            La alfabetización mediática modera esta relación: quienes verifican más información
                            presentan menor reducción de confianza frente a bots, deepfakes o microsegmentación.
                        </div>
                    </div>
                </div>
            </div>
            """
        )
        method_html = """
            <div class="method-grid">
                <div class="method-card">
                    <div class="method-title">Variable dependiente</div>
                    <div class="method-text">Nivel de confianza electoral expresado mediante escala ordinal.</div>
                </div>
                <div class="method-card">
                    <div class="method-title">Variables independientes</div>
                    <div class="method-text">Exposición percibida a IA, automatización, percepción de bots, alfabetización mediática y perfil sociodemográfico.</div>
                </div>
                <div class="method-card">
                    <div class="method-title">Metodología</div>
                    <div class="method-text">CRISP-DM, enfoque cuantitativo descriptivo-exploratorio, modelado predictivo y evidencia digital contextual.</div>
                </div>
            </div>
            """

        st.markdown(method_html, unsafe_allow_html=True)

    with right:
        with st.container(key="card_perfil"):

            st.markdown(
                '<div class="section-title-card">Perfil de la muestra</div>', 
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="section-subtitle-card">Distribución de participantes según género</div>',
                unsafe_allow_html=True,
            )

            gender_col = find_first_existing_column(
                survey_df,
                ["genero", "género", "gender", "sexo"],
            )

            if not survey_df.empty and gender_col:
                gender_df = (
                    survey_df[gender_col]
                    .fillna("No especificado")
                    .astype(str)
                    .value_counts()
                    .reset_index()
                )
                gender_df.columns = ["Género", "Cantidad"]

                fig = px.pie(
                    gender_df,
                    names="Género",
                    values="Cantidad",
                    hole=0.48,
                )

                fig.update_traces(
                    
                    textposition="inside",
                    textinfo="percent",
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Cantidad: %{value}<br>"
                        "Porcentaje: %{percent}<extra></extra>"
                    ),
                )

                fig.update_layout(
                    height=285,
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    margin=dict(l=0, r=0, t=0, b=48),
                    legend_title_text="",
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.08,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=11),
                    ),
                )

                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                empty_state("No se encontró columna de género en el archivo de encuestas.")

    
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # =========================================================
    # ACEPTACIÓN + CONFIANZA
    # =========================================================

    chart1, chart2 = st.columns(2, gap="small")

    with chart1:
        with st.container(key="card_aceptacion"):
            st.markdown(
                '<div class="section-title-card">Aceptación general del uso de IA en política</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="section-subtitle-card">Distribución de respuestas válidas en escala Likert</div>',
                unsafe_allow_html=True,
            )


            perception_col = find_first_existing_column(
                survey_df,
                [
                    "Percepción sobre el uso de IA en campañas políticas [El uso de inteligencia artificial en campañas políticas digitales mejora la comunicación entre partidos y ciudadanos.]_num",
                    "El uso de inteligencia artificial en campañas políticas digitales mejora la comunicación entre partidos y ciudadanos",
                    "mejora la comunicación entre partidos y ciudadanos",
                ],
            )

            if not survey_df.empty and perception_col:
                order = list(LIKERT_LABELS.values())

                values = make_distribution_from_scale(
                    survey_df,
                    perception_col,
                    LIKERT_LABELS,
                    order,
                )

                fig = make_stacked_bar(values, "Aceptación", height=165)

                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    empty_state(
                        "La columna detectada no contiene una escala válida de aceptación."
                    )
            else:
                empty_state("No se encontró una columna de aceptación/percepción de IA.")

            st.markdown(
                """
                <div class="alert-warning">
                    Este indicador resume la actitud general frente al uso de IA en campañas políticas.
                </div>
                """,
                unsafe_allow_html=True,
            )



    with chart2:
        with st.container(key="card_confianza"):
            st.markdown(
                '<div class="section-title-card">Nivel de confianza electoral</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="section-subtitle-card">Percepción posterior al proceso electoral 2025</div>',
                unsafe_allow_html=True,
            )

            confidence_col = find_first_existing_column(
                survey_df,
                [
                    "confianza_idx_round",
                    "confianza_electoral",
                    "nivel_confianza",
                ],
            )

            if not survey_df.empty and confidence_col:
                order = list(CONFIDENCE_LABELS.values())

                conf_df = make_distribution_from_scale(
                    survey_df,
                    confidence_col,
                    CONFIDENCE_LABELS,
                    order,
                )

                fig = make_stacked_bar(conf_df, "Confianza", height=165)

                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    empty_state(
                        "La columna de confianza electoral no contiene una escala 1-5 válida."
                    )
            else:
                empty_state("No se encontró columna de confianza electoral.")

            st.markdown(
                """
                <div class="alert-danger">
                    Este indicador permite observar el estado de la confianza electoral en la muestra analizada.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================
    # REGULACIÓN
    # =========================================================
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    with st.container(key="card_regulacion"):
        st.markdown(
            '<div class="section-title-card">Demanda ciudadana de regulación de IA en campañas</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="section-subtitle-card">
                ¿Considera necesaria una regulación específica para el uso de IA electoral?
            </div>
            """,
            unsafe_allow_html=True,
        )


        regulation_col = find_first_existing_column(
            survey_df,
            [
                "Percepción sobre el uso de IA en campañas políticas [Considero que el uso de inteligencia artificial en campañas políticas debería estar regulado por la ley.]_num",
                "Considero que el uso de inteligencia artificial en campañas políticas debería estar regulado por la ley",
                "debería estar regulado por la ley",
            ],
        )

        if not survey_df.empty and regulation_col:
            order = [
                "Totalmente de acuerdo",
                "De acuerdo",
                "Ni de acuerdo ni en desacuerdo",
                "En desacuerdo",
                "Totalmente en desacuerdo",
            ]

            reg_df = make_distribution_from_scale(
                survey_df,
                regulation_col,
                REGULATION_LABELS,
                order,
            )

            if reg_df.empty:
                empty_state(
                    "La columna detectada no contiene una escala 1-5 válida para regulación."
                )
            else:
                for _, row in reg_df.iterrows():
                    label = row["Respuesta"]
                    pct = float(row["Porcentaje"])
                    count = int(row["Cantidad"])

                    st.markdown(
                        f"""
                        <div class="progress-row">
                            <div class="progress-row-header">
                                <span>{label}</span>
                                <span>{pct:.1f}% · n={count}</span>
                            </div>
                            <div class="progress-track">
                                <div class="progress-fill" style="width:{pct}%;"></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            empty_state("No se encontró columna de regulación de IA.") 
        

    st.markdown(
    """
    <div class="method-note">
        <strong>Nota metodológica:</strong> la encuesta es la fuente principal del análisis.
        Los registros de redes y medios se interpretan como evidencia digital complementaria, no como prueba causal.
    </div>
    """,
    unsafe_allow_html=True,
    )
