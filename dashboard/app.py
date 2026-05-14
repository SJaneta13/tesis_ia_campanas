# dashboard/app.py
import streamlit as st
from pathlib import Path
import pandas as pd


from styles import inject_global_css
from data_loader import (
    load_survey,
    load_news_cases,
    load_latest_metrics,
)
from sections.resumen_general import render_resumen_general
from sections.perfil_muestra import render_perfil_muestra
from sections.conocimiento_ia import render_conocimiento_ia
from sections.percepcion_ciudadana import render_percepcion_ciudadana
from sections.confianza_electoral import render_confianza_electoral
from sections.modelos_predictivos import render_modelos_predictivos
from sections.evidencia_gdelt import render_evidencia_digital


survey_df = load_survey()
news_df = load_news_cases()

def render_sidebar():
    st.sidebar.markdown(
        """
        <div class="sidebar-title">UCE · 2025<br>IA & Política</div>
        <div class="sidebar-subtitle">
            Percepción ciudadana sobre IA en campañas electorales
        </div>
        """,
        unsafe_allow_html=True
    )

    section = st.sidebar.radio(
        "Navegación",
        [
            "Resumen General",
            "Perfil de la muestra",
            "Conocimiento de IA",
            "Percepción ciudadana",
            "Confianza electoral",
            "Modelos predictivos",
            "Evidencia digital GDELT y Encuestas",
            "Triangulación",
            "Datos y artefactos"
        ],
        label_visibility="collapsed"
    )

    st.sidebar.divider()
    st.sidebar.caption("Investigadores:")
    st.sidebar.caption("Silvia Janeta · Cristian Toca")
    st.sidebar.caption("Tutor: Ing. Paulo Llaguno")

    return section


def main():
    st.set_page_config(
        page_title="Plataforma de Resultados - IA en Campañas Políticas",
        page_icon="📊",
        layout="wide"
    )

    inject_global_css()

    survey_df = load_survey()
    news_df = load_news_cases()
    metrics_df = load_latest_metrics()

    section = render_sidebar()

    if section == "Resumen General":
        render_resumen_general(
            survey_df=survey_df,
            news_df=news_df,
            metrics_df=metrics_df
        )

    elif section == "Perfil de la muestra":
        render_perfil_muestra(survey_df)


    elif section == "Conocimiento de IA":
        render_conocimiento_ia(survey_df)

    elif section == "Percepción ciudadana":
        render_percepcion_ciudadana(survey_df)

    elif section == "Confianza electoral":
        render_confianza_electoral(survey_df)

    elif section == "Modelos predictivos":
        render_modelos_predictivos(survey_df)

    elif section == "Evidencia digital GDELT y Encuestas":
        render_evidencia_digital(survey_df, news_df)


    elif section == "Triangulación":
        st.title("Triangulación")
        st.info("Siguiente módulo por construir.")

    elif section == "Datos y artefactos":
        st.title("Datos y artefactos")
        st.info("Siguiente módulo por construir.")


if __name__ == "__main__":
    main()