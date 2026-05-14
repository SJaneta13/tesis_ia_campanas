# dashboard/app.py
import streamlit as st
from pathlib import Path
import pandas as pd
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



st.set_page_config(
    page_title="Plataforma de Resultados - IA en Campañas Políticas",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# FIX GLOBAL PLOTLY RESPONSIVE PARA STREAMLIT CLOUD
# =========================================================
_original_plotly_chart = st.plotly_chart

def responsive_plotly_chart(fig, *args, **kwargs):
    """
    Ajusta todos los gráficos Plotly para que no se corten en Streamlit Cloud.
    No cambia datos ni lógica, solo márgenes, leyenda y render responsivo.
    """
    if hasattr(fig, "update_layout"):
        current_margin = fig.layout.margin

        def safe_margin(value, minimum):
            return max(value if value is not None else 0, minimum)

        fig.update_layout(
            autosize=True,
            margin=dict(
                l=safe_margin(getattr(current_margin, "l", None), 40),
                r=safe_margin(getattr(current_margin, "r", None), 70),
                t=safe_margin(getattr(current_margin, "t", None), 20),
                b=safe_margin(getattr(current_margin, "b", None), 70),
            ),
        )

        fig.update_xaxes(automargin=True)
        fig.update_yaxes(automargin=True)

        # Evita que etiquetas de barras se corten al borde
        try:
            fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
        except Exception:
            pass

        # Donuts/pies: la leyenda lateral se corta en Cloud, mejor abajo
        pie_like = any(
            getattr(trace, "type", None) in ["pie", "sunburst"]
            for trace in getattr(fig, "data", [])
        )

        if pie_like:
            fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.12,
                    xanchor="left",
                    x=0,
                    font=dict(size=11),
                ),
                margin=dict(l=30, r=30, t=20, b=90),
            )

    config = kwargs.pop("config", {}) or {}
    config.update({
        "responsive": True,
        "displayModeBar": False,
    })

    kwargs["config"] = config
    kwargs["use_container_width"] = True

    return _original_plotly_chart(fig, *args, **kwargs)


st.plotly_chart = responsive_plotly_chart



from dashboard.styles import inject_global_css
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