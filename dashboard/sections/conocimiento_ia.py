# dashboard/sections/conocimiento_ia.py
import pandas as pd
import streamlit as st
import plotly.express as px

from components import topbar, kpi_card


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


def clean_category_series(series: pd.Series, default: str = "No especificado"):
    return (
        series.fillna(default)
        .astype(str)
        .str.strip()
        .replace("", default)
    )


def make_category_distribution(
    df: pd.DataFrame,
    col: str,
    label_name: str,
    order: list[str] | None = None,
) -> pd.DataFrame:
    if df.empty or not col or col not in df.columns:
        return pd.DataFrame(columns=[label_name, "Cantidad", "Porcentaje"])

    temp = clean_category_series(df[col])
    counts = temp.value_counts()

    if order:
        counts = counts.reindex(order).fillna(0).astype(int)
        counts = counts[counts > 0]

    out = counts.reset_index()
    out.columns = [label_name, "Cantidad"]

    total = out["Cantidad"].sum()

    if total == 0:
        return pd.DataFrame(columns=[label_name, "Cantidad", "Porcentaje"])

    out["Porcentaje"] = (out["Cantidad"] / total * 100).round(1)

    return out


def empty_state(message: str):
    st.markdown(
        f"""
        <div class="empty-state">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def donut_chart(df: pd.DataFrame, names_col: str, values_col: str, height: int = 315):
    if df.empty:
        return None

    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        hole=0.52,
        color_discrete_sequence=[
            "#0f6fc9",
            "#7cc4f8",
            "#2cb6a4",
            "#facc15",
            "#fb7185",
            "#94a3b8",
        ],
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
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=0, r=0, t=0, b=8),
        legend_title_text="",
        legend=dict(
            orientation="v",
            y=0.72,
            x=1.02,
            font=dict(size=11),
        ),
    )

    return fig


def horizontal_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    text_col: str = "Porcentaje",
    height: int = 315,
):
    if df.empty:
        return None


    plot_df = df.copy()

    fig = px.bar(
        plot_df,
        x=x_col,
        y=y_col,
        orientation="h",
        text=text_col,
        color=y_col,
        color_discrete_sequence=[
            "#0f6fc9",
            "#7cc4f8",
            "#2cb6a4",
            "#facc15",
            "#fb7185",
            "#94a3b8",
        ],
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
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
        margin=dict(l=0, r=45, t=4, b=18),
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        yaxis=dict(title=""),
        showlegend=False,
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


def calculate_positive_count(df: pd.DataFrame, col: str, positives: list[str]) -> int:
    if df.empty or not col or col not in df.columns:
        return 0

    values = clean_category_series(df[col]).str.lower()

    positives_norm = [p.lower().strip() for p in positives]

    return values.isin(positives_norm).sum()


def render_conocimiento_ia(survey_df: pd.DataFrame):
    n_survey = len(survey_df) if not survey_df.empty else 0

    topbar(
        title="Conocimiento de IA",
        subtitle=(
            "Resultados sobre el nivel de conocimiento, reconocimiento y experiencia de los participantes "
            "frente al uso de inteligencia artificial en campañas políticas digitales."
        ),
        pill_text=f"n = {n_survey:,} encuestas" if n_survey else "encuestas no cargadas",
    )

    if survey_df.empty:
        empty_state("No se encontraron datos de encuesta para construir esta sección.")
        return

    # =========================================================
    # Columnas de la Sección 3
    # =========================================================
    escucho_ia_col = find_first_existing_column(
        survey_df,
        [
            "conoce_ia",
            "¿Ha escuchado hablar sobre inteligencia artificial aplicada a campañas políticas digitales?",
            "inteligencia artificial aplicada a campañas políticas digitales",

        ],
    )

    reconocio_col = find_first_existing_column(
        survey_df,

        [
            "percibe_automatizacion",
            "¿Reconoció o notó el uso de herramientas automatizadas (bots, anuncios personalizados, deepfakes, etc.) en la campaña digital de Noboa o González?",
            "herramientas automatizadas",
        ],
    )



    identifica_col = find_first_existing_column(
        survey_df,

        [
            "identifica_ia",
            "¿Sabe identificar cuándo un mensaje, imagen, video o audio político ha sido generado por inteligencia artificial?",
            "sabe identificar",
        ],
    )

    falso_col = find_first_existing_column(
        survey_df,

        [
            "¿Vio alguna vez un video, imagen, audio o noticia política de la campaña entre Luisa González y Daniel Noboa que le pareció “falso”, “manipulado” o generado con IA?",
            "falso",
            "manipulado",
            "generado con IA",
        ],
    )

    detected_vars = sum(
        [
            bool(escucho_ia_col),
            bool(reconocio_col),
            bool(identifica_col),
            bool(falso_col),
        ]
    )

    # =========================================================
    # KPI
    # =========================================================
    conoce_ia = calculate_positive_count(
        survey_df,
        escucho_ia_col,
        ["Sí", "Si"],
    )

    reconoce_herramientas = calculate_positive_count(
        survey_df,
        reconocio_col,
        ["Sí, lo he notado claramente"],
    )

    identifica_facil = calculate_positive_count(
        survey_df,
        identifica_col,
        ["Sí, fácilmente"],
    )

    vio_falso = calculate_positive_count(
        survey_df,
        falso_col,
        ["Sí, muchas veces", "Sí, algunas veces"],
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Conoce IA electoral",
            f"{conoce_ia:,}" if escucho_ia_col else "N/D",
            "Ha escuchado sobre IA en campañas",
            "blue",
        )

    with c2:
        kpi_card(
            "Reconoce automatización",
            f"{reconoce_herramientas:,}" if reconocio_col else "N/D",
            "Detectó bots, deepfakes o anuncios",
            "green",
        )

    with c3:
        kpi_card(
            "Identifica IA",
            f"{identifica_facil:,}" if identifica_col else "N/D",
            "Dice identificar contenido generado",
            "yellow",
        )

    with c4:
        kpi_card(
            "Contenido sospechoso",
            f"{vio_falso:,}" if falso_col else "N/D",
            "Vio contenido falso o manipulado",
            "blue",
        )

    st.markdown('<div class="profile-section-gap"></div>', unsafe_allow_html=True)

    # =========================================================
    # Conocimiento general + reconocimiento
    # =========================================================
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True, key="card_ia_escucho"):
            render_card_header(
                "Conocimiento declarado sobre IA electoral",
                "Participantes que han escuchado hablar sobre inteligencia artificial aplicada a campañas políticas digitales.",
            )

            if escucho_ia_col:
                df_escucho = make_category_distribution(
                    survey_df,
                    escucho_ia_col,
                    "Respuesta",
                    order=["Sí", "No", "No estoy seguro/a"],
                )

                fig = donut_chart(
                    df_escucho,
                    names_col="Respuesta",
                    values_col="Cantidad",
                    height=285,
                )

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                else:
                    empty_state("No existen datos suficientes para graficar conocimiento de IA.")
            else:
                empty_state("No se encontró la columna sobre conocimiento de IA electoral.")

    with col2:
        with st.container(border=True, key="card_ia_reconocio"):
            render_card_header(
                "Reconocimiento de automatización en campaña",
                "Percepción sobre bots, anuncios personalizados, deepfakes u otras herramientas automatizadas.",
            )

            if reconocio_col:
                df_reconocio = make_category_distribution(
                    survey_df,
                    reconocio_col,
                    "Respuesta",
                    order=[
                        "Sí, lo he notado claramente",
                        "Tal vez, pero no estoy seguro/a",
                        "No",
                    ],
                )

                fig = horizontal_bar_chart(
                    df_reconocio,
                    x_col="Cantidad",
                    y_col="Respuesta",
                    text_col="Porcentaje",
                    height=285,
                )

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                else:
                    empty_state("No existen datos suficientes para graficar reconocimiento de automatización.")
            else:
                empty_state("No se encontró la columna sobre herramientas automatizadas.")

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    # =========================================================
    # Identificación + experiencia con contenido falso
    # =========================================================
    col3, col4 = st.columns(2, gap="large")

    with col3:
        with st.container(border=True, key="card_ia_identifica"):
            render_card_header(
                "Capacidad percibida para identificar IA",
                "Nivel declarado para distinguir mensajes, imágenes, videos o audios políticos generados por IA.",
            )

            if identifica_col:
                df_identifica = make_category_distribution(
                    survey_df,
                    identifica_col,
                    "Respuesta",
                    order=[
                        "Sí, fácilmente",
                        "A veces",
                        "No, me resulta difícil distinguirlo",
                    ],
                )

                fig = horizontal_bar_chart(
                    df_identifica,
                    x_col="Cantidad",
                    y_col="Respuesta",
                    text_col="Porcentaje",
                    height=285,
                )

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                else:
                    empty_state("No existen datos suficientes para graficar identificación de IA.")
            else:
                empty_state("No se encontró la columna sobre identificación de contenido generado por IA.")

    with col4:
        with st.container(border=True, key="card_ia_falso"):
            render_card_header(
                "Exposición a contenido político sospechoso",
                "Experiencia con videos, imágenes, audios o noticias percibidas como falsas, manipuladas o generadas con IA.",
            )

            if falso_col:
                df_falso = make_category_distribution(
                    survey_df,
                    falso_col,
                    "Respuesta",
                    order=[
                        "Sí, muchas veces",
                        "Sí, algunas veces",
                        "No",
                        "No estoy seguro/a",
                    ],
                )

                fig = horizontal_bar_chart(
                    df_falso,
                    x_col="Cantidad",
                    y_col="Respuesta",
                    text_col="Porcentaje",
                    height=285,
                )

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                else:
                    empty_state("No existen datos suficientes para graficar exposición a contenido sospechoso.")
            else:
                empty_state("No se encontró la columna sobre contenido falso o manipulado.")

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    # =========================================================
    # Lectura interpretativa
    # =========================================================
    with st.container(border=True, key="card_ia_interpretacion"):
        st.markdown(
            """
            <div class="section-title-card">Lectura interpretativa</div>
            <div class="section-subtitle-card">
                Esta síntesis permite contextualizar el nivel de alfabetización digital e informacional de la muestra frente a la IA electoral.
            </div>
            """,
            unsafe_allow_html=True,
        )

        conocimiento_pct = (conoce_ia / n_survey * 100) if n_survey else 0
        reconocimiento_pct = (reconoce_herramientas / n_survey * 100) if n_survey else 0
        identifica_pct = (identifica_facil / n_survey * 100) if n_survey else 0
        falso_pct = (vio_falso / n_survey * 100) if n_survey else 0

        st.markdown(
            f"""
            <div class="interpretation-grid">
                <div class="interpretation-box blue">
                    <div class="interpretation-value">{conocimiento_pct:.1f}%</div>
                    <div class="interpretation-label">
                        declara haber escuchado sobre IA aplicada a campañas políticas digitales.
                    </div>
                </div>
                <div class="interpretation-box green">
                    <div class="interpretation-value">{reconocimiento_pct:.1f}%</div>
                    <div class="interpretation-label">
                        afirma haber reconocido claramente herramientas automatizadas durante la campaña.
                    </div>
                </div>
                <div class="interpretation-box yellow">
                    <div class="interpretation-value">{identifica_pct:.1f}%</div>
                    <div class="interpretation-label">
                        considera que puede identificar fácilmente contenido político generado por IA.
                    </div>
                </div>
                <div class="interpretation-box red">
                    <div class="interpretation-value">{falso_pct:.1f}%</div>
                    <div class="interpretation-label">
                        reporta haber visto contenido político falso, manipulado o generado con IA.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "Nota metodológica: esta sección describe el conocimiento declarado y la experiencia percibida frente a la IA en campañas digitales. "
        "Los resultados corresponden a autopercepción de los participantes y no a una verificación técnica forense de contenidos."
    )