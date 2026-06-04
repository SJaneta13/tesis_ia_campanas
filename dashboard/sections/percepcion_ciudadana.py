# dashboard/sections/percepcion_ciudadana.py
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


from dashboard.components import topbar, kpi_card

from dashboard.data_loader import (
    load_risk_index_by_age,
    load_deepfake_distrust_by_age,
    load_exposure_index_by_age,
    load_exposure_index_by_age_robust,
)

LIKERT_LABELS = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Ni de acuerdo ni en desacuerdo",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}

LIKERT_ORDER = list(LIKERT_LABELS.values())



LIKERT_COLORS = {
    "Totalmente en desacuerdo": "#1D4ED8",
    "En desacuerdo": "#93C5FD",
    "Ni de acuerdo ni en desacuerdo": "#CBD5E1",
    "De acuerdo": "#99F6E4",
    "Totalmente de acuerdo": "#14B8A6",
}


def find_first_existing_column(df: pd.DataFrame, candidates: list[str]):
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


def empty_state(message: str):
    st.markdown(
        f"""
        <div class="empty-state">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_pct(count: int, total: int) -> float:
    if not total:
        return 0.0
    return round(count / total * 100, 1)


def kpi_value_with_pct(count: int, total: int) -> str:
    if not total:
        return "N/D"
    pct = safe_pct(count, total)
    return f"{pct:.1f}%"


def kpi_help_with_count(count: int, total: int, text: str) -> str:
    if not total:
        return text
    return f"{count:,} de {total:,} · {text}"


def plotly_clean_config() -> dict:
    return {
        "displayModeBar": False,
        "responsive": True,
    }



def render_compact_note(text: str, color: str = "blue"):
    css_class = {
        "blue": "analysis-note-compact",
        "green": "analysis-note-compact-green",
        "yellow": "analysis-note-compact-yellow",
        "red": "analysis-note-compact-red",
    }.get(color, "analysis-note-compact")

    st.markdown(
        f"""
        <div class="{css_class}">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )

def likert_to_numeric(series: pd.Series) -> pd.Series:
    mapping = {
        "totalmente en desacuerdo": 1,
        "en desacuerdo": 2,
        "ni de acuerdo ni en desacuerdo": 3,
        "de acuerdo": 4,
        "totalmente de acuerdo": 5,
    }

    numeric = pd.to_numeric(series, errors="coerce")

    if numeric.notna().sum() > 0:
        return numeric.round()

    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .map(mapping)
    )


def make_likert_distribution(
    df: pd.DataFrame,
    col: str,
) -> pd.DataFrame:
    if df.empty or not col or col not in df.columns:
        return pd.DataFrame(columns=["Respuesta", "Cantidad", "Porcentaje"])

    values = likert_to_numeric(df[col])
    temp = pd.DataFrame({"valor": values})
    temp = temp[temp["valor"].isin(LIKERT_LABELS.keys())].copy()

    if temp.empty:
        return pd.DataFrame(columns=["Respuesta", "Cantidad", "Porcentaje"])

    temp["Respuesta"] = temp["valor"].astype(int).map(LIKERT_LABELS)

    counts = (
        temp["Respuesta"]
        .value_counts()
        .reindex(LIKERT_ORDER)
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

    return out


def positive_count(df: pd.DataFrame, col: str) -> int:
    if df.empty or not col or col not in df.columns:
        return 0

    values = likert_to_numeric(df[col])
    return values.isin([4, 5]).sum()


def negative_count(df: pd.DataFrame, col: str) -> int:
    if df.empty or not col or col not in df.columns:
        return 0

    values = likert_to_numeric(df[col])
    return values.isin([1, 2]).sum()


def make_stacked_bar(values: pd.DataFrame, title_y: str, height: int = 96):
    if values.empty or values["Cantidad"].sum() <= 0:
        return None

    fig = px.bar(
        values,
        x="Porcentaje",
        y=[title_y] * len(values),
        color="Respuesta",
        orientation="h",
        text="Porcentaje",
        category_orders={"Respuesta": LIKERT_ORDER},
        color_discrete_map=LIKERT_COLORS,
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        insidetextanchor="middle",
        cliponaxis=False,
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
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        font=dict(size=11),
    )

    return fig


def make_likert_matrix(items: list[dict], height: int = 420):
    rows = []

    for item in items:
        dist = item["dist"]
        if dist.empty:
            continue

        for _, row in dist.iterrows():
            rows.append(
                {
                    "Indicador": item["short"],
                    "Respuesta": row["Respuesta"],
                    "Porcentaje": row["Porcentaje"],
                    "Cantidad": row["Cantidad"],
                }
            )

    matrix_df = pd.DataFrame(rows)

    if matrix_df.empty:
        return None

    fig = px.bar(
        matrix_df,
        x="Porcentaje",
        y="Indicador",
        color="Respuesta",
        orientation="h",
        text="Porcentaje",
        category_orders={"Respuesta": LIKERT_ORDER},
        color_discrete_map=LIKERT_COLORS,
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        insidetextanchor="middle",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Respuesta: %{customdata[0]}<br>"
            "Cantidad: %{customdata[1]}<br>"
            "Porcentaje: %{x:.1f}%<extra></extra>"
        ),
        customdata=matrix_df[["Respuesta", "Cantidad"]],
    )

    fig.update_layout(
        barmode="stack",
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=0, r=8, t=8, b=68),
        xaxis=dict(
            visible=False,
            range=[0, 100],
        ),
        yaxis=dict(
            title="",
            automargin=True,
            tickfont=dict(size=11, color="#64748b"),
        ),
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="left",
            x=0,
            font=dict(size=10),
        ),
        font=dict(size=11),
    )

    return fig


def render_card_header(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="profile-card-header-soft">
            <div class="section-title-card">{title}</div>
            <div class="section-subtitle-card">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_likert_card(
    title: str,
    subtitle: str,
    df: pd.DataFrame,
    col: str | None,
    y_label: str,
    note: str,
    note_color: str,
    empty_message: str,
):
    render_card_header(title, subtitle)

    if not col:
        empty_state(empty_message)
        return

    dist = make_likert_distribution(df, col)
    fig = make_stacked_bar(dist, y_label, height=96)

    if fig:
        st.plotly_chart(fig, width="stretch", config=plotly_clean_config())

    render_compact_note(note, note_color)


def render_percepcion_ciudadana(survey_df: pd.DataFrame):
    n_survey = len(survey_df) if not survey_df.empty else 0

    topbar(
        title="Percepción ciudadana",
        subtitle=(
            "Análisis de actitudes ciudadanas frente al uso de IA en campañas políticas digitales: aceptación, riesgo"
            "percibido, desconfianza informativa y demanda de regulación."
        ),
        pill_text=f"n = {n_survey:,} encuestas" if n_survey else "encuestas no cargadas",
    )

    if survey_df.empty:
        empty_state("No se encontraron datos de encuesta para construir esta sección.")
        return

    # =========================================================
    # Columnas de percepción ciudadana
    # =========================================================
    mejora_comunicacion_col = find_first_existing_column(
        survey_df,
        [
            "Percepción sobre el uso de IA en campañas políticas [El uso de inteligencia artificial en campañas políticas digitales mejora la comunicación entre partidos y ciudadanos.]_num",
            "mejora_comunicacion",
            "mejora la comunicación entre partidos y ciudadanos",
            "El uso de inteligencia artificial en campañas políticas digitales mejora la comunicación entre partidos y ciudadanos",
        ],
    )

    manipulacion_col = find_first_existing_column(
        survey_df,
        [
            "Percepción sobre el uso de IA en campañas políticas [Los partidos pueden manipular mi opinión mediante mensajes personalizados creados con IA.]_num",
            "manipulacion_opinion",
            "manipular mi opinión",
            "mensajes personalizados creados con IA",
        ],
    )

    bots_confianza_col = find_first_existing_column(
        survey_df,
        [
            "Percepción sobre el uso de IA en campañas políticas [La presencia de bots o cuentas falsas en redes sociales reduce mi confianza en la información política digital.]_num",
            "bots_reduce_confianza",
            "cuentas falsas",
            "reduce mi confianza en la información política digital",
        ],
    )

    transparencia_col = find_first_existing_column(
        survey_df,
        [
            "Percepción sobre el uso de IA en campañas políticas [La inteligencia artificial puede mejorar la transparencia del proceso electoral.]_num",
            "ia_mejora_transparencia",
            "mejorar la transparencia del proceso electoral",
            "transparencia del proceso electoral",
        ],
    )

    deepfakes_col = find_first_existing_column(
        survey_df,
        [
            "Percepción sobre el uso de IA en campañas políticas [La existencia de deepfakes o contenido manipulado me hace desconfiar más de las campañas políticas digitales.]_num",
            "deepfakes_desconfianza",
            "deepfakes",
            "contenido manipulado me hace desconfiar",
        ],
    )

    regulacion_col = find_first_existing_column(
        survey_df,
        [
            "Percepción sobre el uso de IA en campañas políticas [Considero que el uso de inteligencia artificial en campañas políticas debería estar regulado por la ley.]_num",
            "regulacion_ia",
            "debería estar regulado por la ley",
            "regulado por la ley",
        ],
    )

    perception_items = [
        {
            "name": "Mejora la comunicación entre partidos y ciudadanos",
            "short": "Mejora comunicación",
            "col": mejora_comunicacion_col,
        },
        {
            "name": "Los partidos pueden manipular mi opinión mediante mensajes personalizados creados con IA",
            "short": "Riesgo de manipulación",
            "col": manipulacion_col,
        },
        {
            "name": "La presencia de bots o cuentas falsas reduce mi confianza en la información política digital",
            "short": "Bots reducen confianza",
            "col": bots_confianza_col,
        },
        {
            "name": "La IA puede mejorar la transparencia del proceso electoral",
            "short": "Mejora transparencia",
            "col": transparencia_col,
        },
        {
            "name": "Los deepfakes o contenido manipulado aumentan la desconfianza en campañas digitales",
            "short": "Deepfakes generan desconfianza",
            "col": deepfakes_col,
        },
        {
            "name": "El uso de IA en campañas políticas debería estar regulado por la ley",
            "short": "Demanda regulación",
            "col": regulacion_col,
        },
    ]

    for item in perception_items:
        item["dist"] = make_likert_distribution(survey_df, item["col"])

    detected_vars = sum(bool(item["col"]) for item in perception_items)

    # =========================================================
    # KPI
    # =========================================================
    acepta_ia = positive_count(survey_df, mejora_comunicacion_col)
    percibe_manipulacion = positive_count(survey_df, manipulacion_col)
    desconfia_bots = positive_count(survey_df, bots_confianza_col)
    exige_regulacion = positive_count(survey_df, regulacion_col)
    desconfia_deepfakes = positive_count(survey_df, deepfakes_col)


    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        kpi_card(
            "Aceptación funcional",
            kpi_value_with_pct(acepta_ia, n_survey) if mejora_comunicacion_col else "N/D",
            kpi_help_with_count(acepta_ia, n_survey, "cree que la IA mejora la comunicación"),
            "blue",
        )

    with c2:
        kpi_card(
            "Riesgo percibido",
            kpi_value_with_pct(percibe_manipulacion, n_survey) if manipulacion_col else "N/D",
            kpi_help_with_count(percibe_manipulacion, n_survey, "percibe manipulación personalizada"),
            "yellow",
        )

    with c3:
        kpi_card(
            "Desconfianza digital",
            kpi_value_with_pct(desconfia_bots, n_survey) if bots_confianza_col else "N/D",
            kpi_help_with_count(desconfia_bots, n_survey, "afirma que bots reducen confianza"),
            "green",
        )

    with c4:
        kpi_card(
            "Demanda regulación",
            kpi_value_with_pct(exige_regulacion, n_survey) if regulacion_col else "N/D",
            kpi_help_with_count(exige_regulacion, n_survey, "considera necesaria una regulación legal"),
            "blue",
        )     

    st.markdown('<div class="profile-section-gap"></div>', unsafe_allow_html=True)

    # =========================================================
    # Matriz general
    # =========================================================
    with st.container(border=True, key="card_pc_matriz"):
        render_card_header(
            "Mapa general de percepción ciudadana",
            "Distribución comparativa de respuestas en escala Likert para los principales indicadores de percepción sobre IA electoral.",
        )

        fig = make_likert_matrix(perception_items, height=440)

        if fig:
            st.plotly_chart(fig, width="stretch", config=plotly_clean_config())
        else:
            empty_state("No se encontraron columnas suficientes para construir la matriz de percepción.")

    st.markdown('<div class="section-gap-xs"></div>', unsafe_allow_html=True)

    # =========================================================
    # Indicadores específicos
    # =========================================================
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(border=True, key="card_pc_aceptacion"):
            render_likert_card(
                title="Aceptación del uso de IA",
                subtitle="Percepción sobre si la IA mejora la comunicación política entre partidos y ciudadanía.",
                df=survey_df,
                col=mejora_comunicacion_col,
                y_label="Aceptación",
                note="Este indicador resume la actitud favorable hacia el uso funcional de IA en campañas políticas.",
                note_color="blue",
                empty_message="No se encontró la columna sobre mejora de comunicación política mediante IA.",
            )

    with col2:
        with st.container(border=True, key="card_pc_manipulacion"):
            render_likert_card(
                title="Riesgo de manipulación personalizada",
                subtitle="Percepción sobre la influencia mediante mensajes personalizados creados con IA.",
                df=survey_df,
                col=manipulacion_col,
                y_label="Manipulación",
                note="Este indicador representa la preocupación ciudadana frente a la persuasión algorítmica personalizada.",
                note_color="yellow",
                empty_message="No se encontró la columna sobre manipulación mediante IA.",
            )

    st.markdown('<div class="section-gap-xs"></div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="medium")

    with col3:
        with st.container(border=True, key="card_pc_desconfianza"):
            render_card_header(
                "Desconfianza por bots y deepfakes",
                "Comparación del acuerdo agregado frente a bots, cuentas falsas y contenido manipulado.",
            )

            if bots_confianza_col and deepfakes_col:
                bots_pos = positive_count(survey_df, bots_confianza_col)
                deepfakes_pos = positive_count(survey_df, deepfakes_col)

                compare_df = pd.DataFrame(
                    {
                        "Indicador": ["Bots reducen confianza", "Deepfakes generan desconfianza"],
                        "Porcentaje": [
                            safe_pct(bots_pos, n_survey),
                            safe_pct(deepfakes_pos, n_survey),
                        ],
                    }
                )

                fig = px.bar(
                    compare_df,
                    x="Porcentaje",
                    y="Indicador",
                    orientation="h",
                    text="Porcentaje",
                    color="Indicador",
                    color_discrete_map={
                        "Bots reducen confianza": "#1D4ED8",
                        "Deepfakes generan desconfianza": "#14B8A6",
                    },
                )

                fig.update_traces(
                    texttemplate="%{text:.1f}%",
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>%{y}</b><br>Porcentaje: %{x:.1f}%<extra></extra>",
                )

                fig.update_layout(
                    height=130,
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    margin=dict(l=0, r=52, t=2, b=16),
                    xaxis=dict(
                        title="",
                        ticksuffix="%",
                        range=[0, 100],
                        gridcolor="#e5e7eb",
                        zeroline=False,
                    ),
                    yaxis=dict(
                        title="",
                        automargin=True,
                    ),
                    showlegend=False,
                    font=dict(size=11),
                )

                st.plotly_chart(fig, width="stretch", config=plotly_clean_config())

                render_compact_note(
                    "Bots y deepfakes concentran el componente de desconfianza asociado al ecosistema digital electoral.",
                    "red",
                )
            else:
                empty_state("No se encontraron columnas suficientes sobre bots y deepfakes.")

    with col4:
        with st.container(border=True, key="card_pc_regulacion"):
            render_likert_card(
                title="Demanda ciudadana de regulación",
                subtitle="Nivel de acuerdo con que el uso de IA en campañas políticas debería estar regulado por la ley.",
                df=survey_df,
                col=regulacion_col,
                y_label="Regulación",
                note="Este indicador refleja la demanda normativa frente al uso de IA en campañas electorales digitales.",
                note_color="green",
                empty_message="No se encontró la columna sobre regulación de IA.",
            )

    st.markdown('<div class="section-gap-xs"></div>', unsafe_allow_html=True)


    # =========================================================
    # Síntesis interpretativa
    # =========================================================
    with st.container(border=True, key="card_pc_interpretacion"):
        st.markdown(
            """
            <div class="section-title-card">Lectura interpretativa</div>
            <div class="section-subtitle-card">
                La percepción ciudadana combina aceptación funcional de la IA con preocupación por manipulación, desinformación y falta de regulación.
            </div>
            """,
            unsafe_allow_html=True,
        )

        acepta_pct = round(acepta_ia / n_survey * 100, 1) if n_survey else 0
        manipulacion_pct = round(percibe_manipulacion / n_survey * 100, 1) if n_survey else 0
        bots_pct = round(desconfia_bots / n_survey * 100, 1) if n_survey else 0
        regulacion_pct = round(exige_regulacion / n_survey * 100, 1) if n_survey else 0
        deepfakes_pct = round(desconfia_deepfakes / n_survey * 100, 1) if n_survey else 0

        st.markdown(
            f"""
            <div class="interpretation-grid">
                <div class="interpretation-box blue">
                    <div class="interpretation-value">{acepta_pct:.1f}%</div>
                    <div class="interpretation-label">
                        considera que la IA puede mejorar la comunicación entre partidos y ciudadanía.
                    </div>
                </div>
                <div class="interpretation-box yellow">
                    <div class="interpretation-value">{manipulacion_pct:.1f}%</div>
                    <div class="interpretation-label">
                        percibe riesgo de manipulación mediante mensajes personalizados creados con IA.
                    </div>
                </div>
                <div class="interpretation-box red">
                    <div class="interpretation-value">{bots_pct:.1f}%</div>
                    <div class="interpretation-label">
                        afirma que bots o cuentas falsas reducen su confianza; además, el {deepfakes_pct:.1f}% asocia los deepfakes con mayor desconfianza.
                    </div>
                </div>
                <div class="interpretation-box green">
                    <div class="interpretation-value">{regulacion_pct:.1f}%</div>
                    <div class="interpretation-label">
                        considera que el uso de IA en campañas políticas debería estar regulado por la ley.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-gap-xs"></div>', unsafe_allow_html=True)

    # =========================================================
    # Análisis por rangos de edad
    # =========================================================
    with st.container(border=True, key="card_pc_edad_riesgo"):
        render_card_header(
            "Análisis por rangos de edad",
            "Exposición digital, riesgo percibido y desconfianza frente a deepfakes.",
        )

        render_exposure_index_by_age()

        st.markdown('<div class="section-gap-xs"></div>', unsafe_allow_html=True)

        render_risk_index_by_age()

        st.markdown('<div class="section-gap-xs"></div>', unsafe_allow_html=True)

        render_deepfake_distrust_by_age()

    st.caption(
        "Nota metodológica: los indicadores se miden en escala Likert de 1 a 5. "
        "El índice de percepción de riesgo por IA se construyó como el promedio de tres ítems: manipulación mediante mensajes personalizados, "
        "reducción de confianza por bots o cuentas falsas, y desconfianza frente a deepfakes o contenido manipulado. "
        "El índice de exposición digital se construyó a partir de frecuencia de uso de redes sociales, exposición a contenido político digital, "
        "reconocimiento de herramientas automatizadas y exposición a contenido falso o manipulado. "
        "Los rangos con menor tamaño muestral se interpretan como contraste exploratorio."
    )    



def render_analysis_subtitle(title: str, description: str | None = None):
    st.markdown(
        f"""
        <div class="analysis-subsection-header">
            <div class="analysis-subsection-title">{title}</div>
            {f'<div class="analysis-subsection-desc">{description}</div>' if description else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_exposure_index_by_age():
    render_analysis_subtitle(
        "Exposición digital a contenido político",
        "Índice compuesto por uso de redes, recepción de contenido político, reconocimiento de automatización y exposición a contenido falso o manipulado.",
    )

    detailed_df = load_exposure_index_by_age()
    robust_df = load_exposure_index_by_age_robust()

    if detailed_df.empty and robust_df.empty:
        st.warning(
            "No se encontraron archivos de exposición digital. "
            "Ejecuta: python src/06_visualization/survey_age_risk.py"
        )
        return

    tab_robusta, tab_detallada = st.tabs(["Vista robusta", "Vista detallada"])

    with tab_robusta:
        if not robust_df.empty:
            _render_exposure_dot_chart(robust_df)

            render_compact_note(
                "Vista recomendada: agrupa los rangos superiores en 35-64 para reducir la inestabilidad por bajo tamaño muestral.",
                "blue",
            )

    with tab_detallada:
        if not detailed_df.empty:
            _render_exposure_dot_chart(detailed_df)

            render_compact_note(
                "Vista exploratoria: mantiene todos los rangos originales de la encuesta.",
                "blue",
            )


def _render_exposure_dot_chart(df: pd.DataFrame):
    df = df.copy()

    df["etiqueta_eje"] = df.apply(
        lambda row: f"{row['rango_edad']} · n={int(row['n'])}",
        axis=1,
    )

    df["texto_valor"] = df["indice_promedio"].map(lambda x: f"{x:.2f}")

    chart_height = 235 if len(df) <= 3 else 285

    fig = go.Figure()

    fig.add_vrect(
        x0=1,
        x1=2.33,
        fillcolor="#EAF4FF",
        opacity=0.58,
        line_width=0,
        annotation_text="Baja",
        annotation_position="top left",
    )

    fig.add_vrect(
        x0=2.33,
        x1=3.66,
        fillcolor="#FFF7E6",
        opacity=0.58,
        line_width=0,
        annotation_text="Moderada",
        annotation_position="top left",
    )

    fig.add_vrect(
        x0=3.66,
        x1=5,
        fillcolor="#EFFFF7",
        opacity=0.58,
        line_width=0,
        annotation_text="Alta",
        annotation_position="top left",
    )

    fig.add_trace(
        go.Scatter(
            x=df["indice_promedio"],
            y=df["etiqueta_eje"],
            mode="markers+text",
            text=df["texto_valor"],
            textposition="middle right",
            textfont=dict(size=12, color="#64748b"),
            error_x=dict(
                type="data",
                array=df["error_estandar"],
                visible=True,
                thickness=1.3,
                width=4,
                color="#99F6E4",
            ),
            marker=dict(
                size=15,
                color="#14B8A6",
                opacity=0.72,
                line=dict(width=1.4, color="#0F766E"),
            ),
            hovertemplate=(
                "<b>Grupo:</b> %{y}<br>"
                "<b>Índice promedio:</b> %{x:.2f}<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=chart_height,
        margin=dict(l=8, r=36, t=8, b=24),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        showlegend=False,
        xaxis=dict(
            title="Índice promedio de exposición digital",
            range=[1, 5],
            tickvals=[1, 2, 3, 4, 5],
            gridcolor="#E5E7EB",
            zeroline=False,
        ),
        yaxis=dict(
            title="Rango de edad",
            autorange="reversed",
            automargin=True,
        ),
        font=dict(size=12, color="#64748b"),
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config=plotly_clean_config(),
    )


def render_risk_index_by_age():

    render_analysis_subtitle(
    "Índice de percepción de riesgo por IA",
    "Promedio de tres ítems: manipulación mediante mensajes personalizados, reducción de confianza por bots y desconfianza frente a deepfakes.",
    )

    df = load_risk_index_by_age()

    if df.empty:
        st.warning(
            "No se encontró el archivo risk_index_by_age.csv. "
            "Ejecuta: python src/06_visualization/survey_age_risk.py"
        )
        return

    df = df.copy()

    age_order = ["18-24", "25-34", "35-44", "45-54", "55-64"]
    df["rango_edad"] = pd.Categorical(
        df["rango_edad"],
        categories=age_order,
        ordered=True,
    )

    df = df.sort_values("rango_edad")

    df["etiqueta_eje"] = df.apply(
        lambda row: f"{row['rango_edad']}  ·  n={int(row['n'])}",
        axis=1,
    )

    df["texto_valor"] = df["indice_promedio"].map(lambda x: f"{x:.2f}")

    fig = go.Figure()

    # Bandas interpretativas
    fig.add_vrect(
        x0=1,
        x1=2.33,
        fillcolor="#EAF4FF",
        opacity=0.65,
        line_width=0,
        annotation_text="Bajo",
        annotation_position="top left",
    )

    fig.add_vrect(
        x0=2.33,
        x1=3.66,
        fillcolor="#FFF7E6",
        opacity=0.65,
        line_width=0,
        annotation_text="Moderado",
        annotation_position="top left",
    )

    fig.add_vrect(
        x0=3.66,
        x1=5,
        fillcolor="#FFECEC",
        opacity=0.65,
        line_width=0,
        annotation_text="Alto",
        annotation_position="top left",
    )

    fig.add_trace(
        go.Scatter(
            x=df["indice_promedio"],
            y=df["etiqueta_eje"],
            mode="markers+text",
            text=df["texto_valor"],
            textposition="middle right",
            error_x=dict(
                type="data",
                array=df["error_estandar"],
                visible=True,
                thickness=1.4,
                width=4,
            ),
            marker=dict(
                size=16,
                color="#2563EB",
                line=dict(width=1.5, color="#1E3A8A"),
            ),
            hovertemplate=(
                "<b>Rango de edad:</b> %{y}<br>"
                "<b>Índice promedio:</b> %{x:.2f}<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=285,
        margin=dict(l=8, r=36, t=8, b=24),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        showlegend=False,
        xaxis=dict(
            title="Índice promedio de percepción de riesgo por IA",
            range=[1, 5],
            tickvals=[1, 2, 3, 4, 5],
            gridcolor="#E5E7EB",
        ),
        yaxis=dict(
            title="Rango de edad",
            autorange="reversed",
        ),
        font=dict(size=13),
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config=plotly_clean_config(),
    )


    st.markdown(
        """
        <div class="alert-info-blue">
            Lectura: el índice promedio se mantiene en niveles moderados en la mayoría de rangos etarios. 
            El grupo de 35-44 años presenta el valor más alto del índice, ubicándose en la zona de percepción alta; 
            no obstante, por su menor tamaño muestral, este resultado debe analizarse como una tendencia exploratoria.

        </div>
        """,
        unsafe_allow_html=True,


    )


def render_deepfake_distrust_by_age():

    render_analysis_subtitle(
    "Deepfakes y desconfianza",
    "Distribución agrupada de respuestas en desacuerdo, neutral y acuerdo frente a contenidos políticos manipulados o generados con IA.",
    )

    df = load_deepfake_distrust_by_age()

    if df.empty:
        st.warning(
            "No se encontró el archivo deepfake_distrust_by_age.csv. "
            "Ejecuta: python src/06_visualization/survey_age_risk.py"
        )
        return

    df = df.copy()

    # Agrupación visual de la escala Likert para dashboard
    category_map = {
        1: "Desacuerdo",
        2: "Desacuerdo",
        3: "Neutral",
        4: "Acuerdo",
        5: "Acuerdo",
    }

    category_order = ["Desacuerdo", "Neutral", "Acuerdo"]
    age_order = ["18-24", "25-34", "35-44", "45-54", "55-64"]

    df["categoria_resumida"] = df["respuesta_valor"].map(category_map)

    grouped = (
        df.groupby(["rango_edad", "categoria_resumida"], observed=True)
        .agg(
            frecuencia=("frecuencia", "sum"),
            total_rango=("total_rango", "max"),
        )
        .reset_index()
    )

    grouped["porcentaje"] = (
        grouped["frecuencia"] / grouped["total_rango"] * 100
    ).round(1)

    grouped["rango_edad"] = pd.Categorical(
        grouped["rango_edad"],
        categories=age_order,
        ordered=True,
    )

    grouped["categoria_resumida"] = pd.Categorical(
        grouped["categoria_resumida"],
        categories=category_order,
        ordered=True,
    )

    grouped = grouped.sort_values(["rango_edad", "categoria_resumida"])

    totals = (
        grouped[["rango_edad", "total_rango"]]
        .drop_duplicates()
        .sort_values("rango_edad")
    )

    label_map = {
        row["rango_edad"]: f"{row['rango_edad']} · n={int(row['total_rango'])}"
        for _, row in totals.iterrows()
    }

    grouped["etiqueta_eje"] = grouped["rango_edad"].map(label_map)

    color_map = {
        "Desacuerdo": "#60A5FA",
        "Neutral": "#CBD5E1",
        "Acuerdo": "#14B8A6",
    }

    fig = px.bar(
        grouped,
        x="porcentaje",
        y="etiqueta_eje",
        color="categoria_resumida",
        orientation="h",
        barmode="stack",
        text=grouped["porcentaje"].map(lambda x: f"{x:.1f}%" if x >= 7 else ""),
        category_orders={
            "categoria_resumida": category_order,
        },
        color_discrete_map=color_map,
        labels={
            "porcentaje": "Porcentaje de respuestas",
            "etiqueta_eje": "Rango de edad",
            "categoria_resumida": "Respuesta agrupada",
        },
    )

    fig.update_layout(
        height=300,
        margin=dict(l=8, r=24, t=8, b=24),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        legend_title_text="Respuesta agrupada",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            range=[0, 100],
            ticksuffix="%",
            gridcolor="#E5E7EB",
            title="Porcentaje de respuestas",
        ),
        yaxis=dict(
            title="Rango de edad",
            autorange="reversed",
        ),
        font=dict(size=13),
    )

    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle",
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config=plotly_clean_config(),
    )


    acuerdo_df = grouped[grouped["categoria_resumida"] == "Acuerdo"].copy()

    if not acuerdo_df.empty:
        max_row = acuerdo_df.loc[acuerdo_df["porcentaje"].idxmax()]
        st.markdown(
            f"""
            <div class="alert-info-blue">
                Lectura: el mayor porcentaje de acuerdo frente a la afirmación sobre deepfakes y desconfianza 
                se observa en el rango <b>45-54</b>, con <b>76.2%</b>. Este resultado sugiere una mayor preocupación 
                ante contenidos políticos manipulados o generados con IA en dicho grupo; sin embargo, debe interpretarse 
                como contraste exploratorio debido al menor tamaño muestral del grupo.
            </div>
            """,
            unsafe_allow_html=True,
        )    