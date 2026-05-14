# dashboard/sections/percepcion_ciudadana.py
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from components import topbar, kpi_card


LIKERT_LABELS = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Ni de acuerdo ni en desacuerdo",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}

LIKERT_ORDER = list(LIKERT_LABELS.values())

LIKERT_COLORS = {
    "Totalmente en desacuerdo": "#0f6fc9",
    "En desacuerdo": "#7cc4f8",
    "Ni de acuerdo ni en desacuerdo": "#ff2d2d",
    "De acuerdo": "#fca5a5",
    "Totalmente de acuerdo": "#2cb6a4",
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


def make_stacked_bar(values: pd.DataFrame, title_y: str, height: int = 175):
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


def make_likert_matrix(items: list[dict], height: int = 430):
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
        margin=dict(l=0, r=10, t=10, b=70),
        xaxis=dict(
            visible=False,
            range=[0, 100],
        ),
        yaxis=dict(
            title="",
            automargin=True,
            tickfont=dict(size=11),
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


def render_percepcion_ciudadana(survey_df: pd.DataFrame):
    n_survey = len(survey_df) if not survey_df.empty else 0

    topbar(
        title="Percepción ciudadana",
        subtitle=(
            "Análisis de actitudes frente al uso de inteligencia artificial en campañas políticas digitales: "
            "aceptación, riesgo percibido, confianza informativa y demanda de regulación."
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

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Aceptación funcional",
            f"{acepta_ia:,}" if mejora_comunicacion_col else "N/D",
            "Cree que la IA mejora la comunicación",
            "blue",
        )

    with c2:
        kpi_card(
            "Riesgo percibido",
            f"{percibe_manipulacion:,}" if manipulacion_col else "N/D",
            "Percibe manipulación personalizada",
            "yellow",
        )

    with c3:
        kpi_card(
            "Desconfianza digital",
            f"{desconfia_bots:,}" if bots_confianza_col else "N/D",
            "Bots reducen confianza informativa",
            "green",
        )

    with c4:
        kpi_card(
            "Demanda regulación",
            f"{exige_regulacion:,}" if regulacion_col else "N/D",
            "Considera necesaria una regulación legal",
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
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            empty_state("No se encontraron columnas suficientes para construir la matriz de percepción.")

    st.markdown('<div class="section-gap-xs"></div>', unsafe_allow_html=True)

    # =========================================================
    # Aceptación + manipulación
    # =========================================================
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True, key="card_pc_aceptacion"):
            render_card_header(
                "Aceptación del uso de IA",
                "Percepción sobre si la inteligencia artificial mejora la comunicación política entre partidos y ciudadanía.",
            )

            if mejora_comunicacion_col:
                dist = make_likert_distribution(survey_df, mejora_comunicacion_col)
                fig = make_stacked_bar(dist, "Aceptación", height=165)

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown(
                    """
                    <div class="alert-info-blue">
                        Este indicador resume la actitud favorable hacia el uso funcional de IA en campañas políticas.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna sobre mejora de comunicación política mediante IA.")

    with col2:
        with st.container(border=True, key="card_pc_manipulacion"):
            render_card_header(
                "Riesgo de manipulación personalizada",
                "Percepción sobre la capacidad de los partidos para influir en la opinión mediante mensajes personalizados creados con IA.",
            )

            if manipulacion_col:
                dist = make_likert_distribution(survey_df, manipulacion_col)
                fig = make_stacked_bar(dist, "Manipulación", height=165)

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown(
                    """
                    <div class="alert-warning">
                        Este indicador representa la preocupación ciudadana frente a la persuasión algorítmica personalizada.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna sobre manipulación mediante IA.")

    st.markdown('<div class="section-gap-xs"></div>', unsafe_allow_html=True)

    # =========================================================
    # Bots/deepfakes + regulación
    # =========================================================
    col3, col4 = st.columns(2, gap="large")

    with col3:
        with st.container(border=True, key="card_pc_desconfianza"):
            render_card_header(
                "Desconfianza por bots y deepfakes",
                "Percepción del impacto de cuentas falsas, bots y contenido manipulado sobre la confianza en la información política digital.",
            )

            if bots_confianza_col and deepfakes_col:
                bots_pos = positive_count(survey_df, bots_confianza_col)
                deepfakes_pos = positive_count(survey_df, deepfakes_col)

                compare_df = pd.DataFrame(
                    {
                        "Indicador": ["Bots reducen confianza", "Deepfakes generan desconfianza"],
                        "Cantidad": [bots_pos, deepfakes_pos],
                        "Porcentaje": [
                            round(bots_pos / n_survey * 100, 1) if n_survey else 0,
                            round(deepfakes_pos / n_survey * 100, 1) if n_survey else 0,
                        ],
                    }
                )

                fig = px.bar(
                    compare_df,
                    x="Cantidad",
                    y="Indicador",
                    orientation="h",
                    text="Porcentaje",
                    color="Indicador",
                    color_discrete_sequence=["#0f6fc9", "#fb7185"],
                )

                fig.update_traces(
                    texttemplate="%{text:.1f}%",
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Cantidad: %{x}<br>"
                        "Porcentaje: %{text:.1f}%<extra></extra>"
                        
                    ),
                )


                fig.update_layout(
                    height=190,
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    margin=dict(l=0, r=60, t=4, b=18),
                    xaxis=dict(
                        title="",
                        showgrid=True,
                        gridcolor="#e5e7eb",
                        zeroline=False,
                        range=[0, n_survey],
                    ),
                    yaxis=dict(
                        title="",
                        automargin=True,
                    ),
                    showlegend=False,
                    font=dict(size=11),
                )



                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown(
                    """
                    <div class="alert-danger">
                        Los indicadores de bots y deepfakes permiten observar el componente de desconfianza asociado al ecosistema digital electoral.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontraron columnas suficientes sobre bots y deepfakes.")

    with col4:
        with st.container(border=True, key="card_pc_regulacion"):
            render_card_header(
                "Demanda ciudadana de regulación",
                "Nivel de acuerdo con que el uso de IA en campañas políticas debería estar regulado por la ley.",
            )

            if regulacion_col:
                dist = make_likert_distribution(survey_df, regulacion_col)
                fig = make_stacked_bar(dist, "Regulación", height=165)

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown(
                    """
                    <div class="alert-info-green">
                        Este indicador refleja la demanda normativa frente al uso de IA en campañas electorales digitales.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna sobre regulación de IA.")

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
                        afirma que bots o cuentas falsas reducen su confianza; además, el 55.8% asocia los deepfakes con mayor desconfianza.
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

    st.caption(
        "Nota metodológica: esta sección corresponde a indicadores de percepción ciudadana medidos en escala Likert. "
        "Los porcentajes positivos agrupan las respuestas 'De acuerdo' y 'Totalmente de acuerdo'."
    )