# dashboard/sections/conocimiento_ia.py


import plotly.express as px

import pandas as pd
import streamlit as st

from dashboard.data_loader import (
    load_h1_spearman_sensitivity,
)

from dashboard.components import topbar, kpi_card
from dashboard.common import (
    PLOTLY_CONFIG,
    find_first_existing_column,
    empty_state,
    clean_category_series,
    make_category_distribution,
    donut_chart,
    horizontal_bar_chart,
    render_card_header,
    safe_pct,
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
            '¿Vio alguna vez un video, imagen, audio o noticia política de la campaña entre Luisa González y Daniel Noboa que le pareció "falso", "manipulado" o generado con IA?',
            "falso",
            "manipulado",
            "generado con IA",
        ],
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
            f"{safe_pct(conoce_ia, n_survey):.1f}%" if escucho_ia_col else "N/D",
            f"{conoce_ia:,} de {n_survey:,} participantes",
            "blue",
        )

    with c2:
        kpi_card(
            "Reconoce automatización",
            f"{safe_pct(reconoce_herramientas, n_survey):.1f}%" if reconocio_col else "N/D",
            f"{reconoce_herramientas:,} de {n_survey:,} participantes",
            "green",
        )

    with c3:
        kpi_card(
            "Identifica facilmente IA",
            f"{safe_pct(identifica_facil, n_survey):.1f}%" if identifica_col else "N/D",
            f"{identifica_facil:,} de {n_survey:,} participantes",
            "yellow",
        )

    with c4:
        kpi_card(
            "Percibe Contenido sospechoso",
            f"{safe_pct(vio_falso, n_survey):.1f}%" if falso_col else "N/D",
            f"{vio_falso:,} de {n_survey:,} participantes",
            "purple",
        )

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # =========================================================
    # Conocimiento general + reconocimiento
    # =========================================================
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(key="card_ia_escucho"):
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
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    empty_state("No existen datos suficientes para graficar conocimiento de IA.")
            else:
                empty_state("No se encontró la columna sobre conocimiento de IA electoral.")

    with col2:
        with st.container(key="card_ia_reconocio"):
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
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    empty_state("No existen datos suficientes para graficar reconocimiento de automatización.")
            else:
                empty_state("No se encontró la columna sobre herramientas automatizadas.")

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # =========================================================
    # Identificación + experiencia con contenido falso
    # =========================================================
    col3, col4 = st.columns(2, gap="medium")

    with col3:
        with st.container(key="card_ia_identifica"):
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
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    empty_state("No existen datos suficientes para graficar identificación de IA.")
            else:
                empty_state("No se encontró la columna sobre identificación de contenido generado por IA.")

    with col4:
        with st.container(key="card_ia_falso"):
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
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    empty_state("No existen datos suficientes para graficar exposición a contenido sospechoso.")
            else:
                empty_state("No se encontró la columna sobre contenido falso o manipulado.")

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # =========================================================
    # Lectura interpretativa
    # =========================================================
    with st.container(key="card_ia_interpretacion"):
        st.markdown(
            """
            <div class="section-title-card">Lectura interpretativa</div>
            <div class="section-subtitle-card">
                Esta síntesis resume la diferencia entre conocimiento declarado, reconocimiento de automatización, capacidad de identificación y exposición percibida a contenido sospechoso.
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

    st.markdown(
    """
    <div class="ia-method-note">
        <strong>Nota metodológica:</strong> esta sección describe el conocimiento declarado y la experiencia percibida
        frente a la IA en campañas digitales. Los resultados corresponden a autopercepción de los participantes
        y no a una verificación técnica forense de contenidos.
    </div>
    """,
    unsafe_allow_html=True,
)
