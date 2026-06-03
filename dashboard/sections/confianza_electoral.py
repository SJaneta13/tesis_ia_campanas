import pandas as pd
import streamlit as st
import plotly.express as px

from dashboard.components import topbar, kpi_card


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


def make_likert_distribution(df: pd.DataFrame, col: str) -> pd.DataFrame:
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

    return pd.DataFrame(
        {
            "Respuesta": counts.index,
            "Cantidad": counts.values,
            "Porcentaje": (counts.values / total * 100).round(1),
        }
    )


def positive_count(df: pd.DataFrame, col: str) -> int:
    if df.empty or not col or col not in df.columns:
        return 0

    values = likert_to_numeric(df[col])
    return values.isin([4, 5]).sum()


def make_stacked_bar(values: pd.DataFrame, title_y: str, height: int = 165):
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
        xaxis=dict(visible=False, range=[0, 100]),
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


def make_category_bar(df: pd.DataFrame, col: str, order: list[str], height: int = 220):
    if df.empty or not col or col not in df.columns:
        return None

    counts = (
        df[col]
        .fillna("No registrado")
        .astype(str)
        .str.strip()
        .value_counts()
        .reindex(order)
        .dropna()
        .astype(int)
    )

    total = counts.sum()

    if total == 0:
        return None

    chart_df = pd.DataFrame(
        {
            "Categoría": counts.index,
            "Cantidad": counts.values,
            "Porcentaje": (counts.values / total * 100).round(1),
        }
    )

    fig = px.bar(
        chart_df,
        x="Cantidad",
        y="Categoría",
        orientation="h",
        text="Porcentaje",
        color="Categoría",
        color_discrete_sequence=["#0f6fc9", "#7cc4f8", "#ff2d2d", "#fca5a5", "#2cb6a4"],
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
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=0, r=55, t=4, b=18),
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#e5e7eb",
            zeroline=False,
            range=[0, total],
        ),
        yaxis=dict(title="", automargin=True),
        showlegend=False,
        font=dict(size=11),
    )

    return fig


def make_likert_matrix(items: list[dict], height: int = 340):
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
        xaxis=dict(visible=False, range=[0, 100]),
        yaxis=dict(title="", automargin=True, tickfont=dict(size=11)),
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.14,
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


def render_confianza_electoral(survey_df: pd.DataFrame):
    n_survey = len(survey_df) if not survey_df.empty else 0

    topbar(
        title="Confianza electoral",
        subtitle=(
            "Análisis de la confianza ciudadana frente al proceso electoral y su posible afectación "
            "por bots, deepfakes, manipulación mediante IA e influencia digital en la decisión de voto."
        ),
        pill_text=f"n = {n_survey:,} encuestas" if n_survey else "encuestas no cargadas",
    )

    if survey_df.empty:
        empty_state("No se encontraron datos de encuesta para construir esta sección.")
        return

    limpieza_col = find_first_existing_column(
        survey_df,
        [
            "confianza_limpieza",
            "limpieza",
            "transparencia del proceso electoral",
            "confianza en la limpieza",
        ],
    )

    fraude_col = find_first_existing_column(
        survey_df,
        [
            "confianza_fraude",
            "fraude",
            "manipulación electoral",
        ],
    )

    influencia_voto_col = find_first_existing_column(
        survey_df,
        [
            "¿Considera que el uso de IA en campañas digitales influyó en su decisión de voto en las elecciones presidenciales de 2025?",
            "influyó en su decisión de voto",
            "decision de voto",
            "decisión de voto",
        ],
    )

    cambio_confianza_col = find_first_existing_column(
        survey_df,
        [
            "¿Ha cambiado su confianza en el proceso electoral al saber que existen bots, deepfakes o manipulación mediante IA?",
            "ha cambiado su confianza",
            "ahora confío menos",
            "bots, deepfakes o manipulación mediante IA",
        ],
    )

    indice_col = find_first_existing_column(
        survey_df,
        [
            "confianza_idx_round",
            "confianza_idx",
        ],
    )

    confianza_items = [
        {
            "name": "Confianza en la limpieza o transparencia del proceso electoral",
            "short": "Limpieza electoral",
            "col": limpieza_col,
        },
        {
            "name": "Percepción de fraude o manipulación electoral",
            "short": "Riesgo de fraude",
            "col": fraude_col,
        },
    ]

    for item in confianza_items:
        item["dist"] = make_likert_distribution(survey_df, item["col"])

    confianza_limpieza = positive_count(survey_df, limpieza_col)
    percibe_fraude = positive_count(survey_df, fraude_col)

    if influencia_voto_col:
        influyo_voto = (
            survey_df[influencia_voto_col]
            .fillna("")
            .astype(str)
            .str.strip()
            .isin(["Sí, algo", "Sí, mucho"])
            .sum()
        )
    else:
        influyo_voto = 0

    if cambio_confianza_col:
        confia_menos = (
            survey_df[cambio_confianza_col]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("Sí, ahora confío menos")
            .sum()
        )
    else:
        confia_menos = 0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Confianza positiva",
            f"{confianza_limpieza:,}" if limpieza_col else "N/D",
            "Confía en la limpieza del proceso",
            "blue",
        )

    with c2:
        kpi_card(
            "Riesgo percibido",
            f"{percibe_fraude:,}" if fraude_col else "N/D",
            "Percibe fraude o manipulación",
            "red",
        )

    with c3:
        kpi_card(
            "Influencia en voto",
            f"{influyo_voto:,}" if influencia_voto_col else "N/D",
            "Reconoce influencia de IA en su decisión",
            "yellow",
        )

    with c4:
        kpi_card(
            "Confianza reducida",
            f"{confia_menos:,}" if cambio_confianza_col else "N/D",
            "Confía menos por bots/deepfakes/IA",
            "green",
        )

    st.markdown('<div class="profile-section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_ce_matriz"):
        render_card_header(
            "Mapa de confianza electoral",
            "Distribución comparativa de los indicadores Likert asociados a limpieza electoral y riesgo de fraude o manipulación.",
        )

        fig = make_likert_matrix(confianza_items, height=330)

        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            empty_state("No se encontraron columnas suficientes para construir la matriz de confianza electoral.")

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True, key="card_ce_limpieza"):
            render_card_header(
                "Confianza en la limpieza electoral",
                "Nivel de acuerdo con una percepción positiva sobre la limpieza o transparencia del proceso electoral.",
            )

            if limpieza_col:
                dist = make_likert_distribution(survey_df, limpieza_col)
                fig = make_stacked_bar(dist, "Limpieza electoral", height=165)

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown(
                    """
                    <div class="alert-info-blue">
                        Este indicador permite observar el componente positivo de confianza institucional frente al proceso electoral.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna de confianza en limpieza electoral.")

    with col2:
        with st.container(border=True, key="card_ce_fraude"):
            render_card_header(
                "Percepción de fraude o manipulación",
                "Nivel de acuerdo con la posibilidad de fraude, manipulación o alteración del proceso electoral.",
            )

            if fraude_col:
                dist = make_likert_distribution(survey_df, fraude_col)
                fig = make_stacked_bar(dist, "Fraude/manipulación", height=165)

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown(
                    """
                    <div class="alert-danger">
                        Este indicador refleja la dimensión crítica de la confianza electoral: sospecha, incertidumbre o percepción de manipulación.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna de percepción de fraude o manipulación.")

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="large")

    with col3:
        with st.container(border=True, key="card_ce_influencia_voto"):
            render_card_header(
                "Influencia de IA en la decisión de voto",
                "Percepción ciudadana sobre si el uso de IA en campañas digitales influyó en su decisión electoral.",
            )

            if influencia_voto_col:
                order = ["Nada", "Poco", "Sí, algo", "Sí, mucho", "No sé/no aplica"]
                fig = make_category_bar(survey_df, influencia_voto_col, order, height=225)

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown(
                    """
                    <div class="alert-warning">
                        Este indicador conecta la exposición a campañas digitales con una posible incidencia subjetiva en la decisión de voto.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna sobre influencia de IA en la decisión de voto.")

    with col4:
        with st.container(border=True, key="card_ce_cambio_confianza"):
            render_card_header(
                "Cambio de confianza por IA",
                "Variación de la confianza en el proceso electoral al conocer la existencia de bots, deepfakes o manipulación mediante IA.",
            )

            if cambio_confianza_col:
                order = ["Sí, ahora confío menos", "No ha cambiado", "Sí, ahora confío más", "No sé"]
                fig = make_category_bar(survey_df, cambio_confianza_col, order, height=225)

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown(
                    """
                    <div class="alert-info-green">
                        Este indicador muestra si las prácticas digitales asociadas a IA erosionan, mantienen o refuerzan la confianza electoral.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna sobre cambio de confianza electoral.")

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_ce_interpretacion"):
        st.markdown(
            """
            <div class="section-title-card">Lectura interpretativa</div>
            <div class="section-subtitle-card">
                La confianza electoral se interpreta a partir de la tensión entre confianza institucional, percepción de fraude,
                influencia digital en el voto y reducción de confianza ante bots, deepfakes o manipulación mediante IA.
            </div>
            """,
            unsafe_allow_html=True,
        )

        limpieza_pct = round(confianza_limpieza / n_survey * 100, 1) if n_survey else 0
        fraude_pct = round(percibe_fraude / n_survey * 100, 1) if n_survey else 0
        influyo_pct = round(influyo_voto / n_survey * 100, 1) if n_survey else 0
        confia_menos_pct = round(confia_menos / n_survey * 100, 1) if n_survey else 0

        st.markdown(
            f"""
            <div class="interpretation-grid">
                <div class="interpretation-box blue">
                    <div class="interpretation-value">{limpieza_pct:.1f}%</div>
                    <div class="interpretation-label">
                        expresa una percepción favorable sobre la limpieza o transparencia del proceso electoral.
                    </div>
                </div>
                <div class="interpretation-box red">
                    <div class="interpretation-value">{fraude_pct:.1f}%</div>
                    <div class="interpretation-label">
                        percibe riesgo de fraude, manipulación o alteración del proceso electoral.
                    </div>
                </div>
                <div class="interpretation-box yellow">
                    <div class="interpretation-value">{influyo_pct:.1f}%</div>
                    <div class="interpretation-label">
                        considera que la IA influyó algo o mucho en su decisión de voto.
                    </div>
                </div>
                <div class="interpretation-box green">
                    <div class="interpretation-value">{confia_menos_pct:.1f}%</div>
                    <div class="interpretation-label">
                        afirma que ahora confía menos al conocer la existencia de bots, deepfakes o manipulación mediante IA.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "Nota metodológica: la confianza electoral se analiza mediante indicadores Likert y preguntas categóricas. "
        "En los indicadores Likert, los porcentajes positivos agrupan 'De acuerdo' y 'Totalmente de acuerdo'."
    )