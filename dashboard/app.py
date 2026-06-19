# dashboard/app.py
import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


st.set_page_config(
    page_title="UCE · IA y Política",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard.styles import inject_global_css
from dashboard.filters import render_global_filters
from dashboard.data_loader import (
    load_survey,
    load_news_cases,
    load_latest_metrics,
)


from dashboard.sections.resumen_general import render_resumen_general
from dashboard.sections.perfil_muestra import render_perfil_muestra
from dashboard.sections.conocimiento_ia import render_conocimiento_ia
from dashboard.sections.percepcion_ciudadana import render_percepcion_ciudadana
from dashboard.sections.confianza_electoral import render_confianza_electoral
from dashboard.sections.modelos_predictivos import render_modelos_predictivos
from dashboard.sections.evidencia_gdelt import render_evidencia_digital
from dashboard.sections.datos_artefactos import render_datos_artefactos


def render_sidebar_header():
    st.sidebar.markdown(
        """
        <div class="sidebar-title">UCE · 2025<br>IA & Política</div>
        <div class="sidebar-subtitle">
            Percepción ciudadana sobre IA en campañas electorales
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_navigation():
    return st.sidebar.radio(
        "Navegación",
        [
            "Resumen General",
            "Perfil de la muestra",
            "Conocimiento de IA",
            "Percepción ciudadana",
            "Confianza electoral",
            "Modelos predictivos",
            "Evidencia digital y triangulación",
            "Datos y artefactos",
        ],
        label_visibility="collapsed",
    )


def render_sidebar_footer():
    st.sidebar.divider()
    st.sidebar.caption("Investigadores:")
    st.sidebar.caption("Silvia Janeta · Cristian Toca")
    st.sidebar.caption("Tutor: Ing. Paulo Llaguno")


def main():
    inject_global_css()

    survey_df = load_survey()
    news_df = load_news_cases()
    metrics_df = load_latest_metrics()

    render_sidebar_header()
    section = render_sidebar_navigation()

    survey_df_filtered, active_filters = render_global_filters(survey_df)

    render_sidebar_footer()

    if section == "Resumen General":
        render_resumen_general(
            survey_df=survey_df_filtered,
            news_df=news_df,
            metrics_df=metrics_df,
        )

    elif section == "Perfil de la muestra":
        render_perfil_muestra(survey_df_filtered)

    elif section == "Conocimiento de IA":
        render_conocimiento_ia(survey_df_filtered)

    elif section == "Percepción ciudadana":
        render_percepcion_ciudadana(survey_df_filtered)

    elif section == "Confianza electoral":
        render_confianza_electoral(survey_df_filtered)

    elif section == "Modelos predictivos":
        render_modelos_predictivos(survey_df)

    elif section == "Evidencia digital y triangulación":
        render_evidencia_digital(survey_df_filtered, news_df)

    elif section == "Datos y artefactos":
        render_datos_artefactos(
            survey_df=survey_df,
            survey_df_filtered=survey_df_filtered,
            news_df=news_df,
            metrics_df=metrics_df,
        )

if __name__ == "__main__":
    main()