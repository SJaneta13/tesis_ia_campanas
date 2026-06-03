# dashboard/styles.py
import streamlit as st


def inject_global_css():
    st.markdown("""
<style>
.stApp {
    background-color: #f6f8fb;
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
    max-width: 1320px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
}

.sidebar-title {
    font-size: 1.1rem;
    font-weight: 850;
    color: #1e3a8a;
    margin-bottom: 0.1rem;
}

.sidebar-subtitle {
    font-size: 0.82rem;
    color: #64748b;
    line-height: 1.35;
    margin-bottom: 1.2rem;
}

/* Topbar */
.topbar {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 18px 22px;
    margin-bottom: 18px;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04);
    position: relative;
}

.topbar-title {
    font-size: 1.45rem;
    font-weight: 850;
    color: #0f172a;
    margin-bottom: 4px;
}

.topbar-subtitle {
    color: #64748b;
    font-size: 0.93rem;
    line-height: 1.45;
    max-width: 850px;
}

.topbar-pill {
    position: absolute;
    right: 22px;
    top: 18px;
}

.small-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    color: #64748b;
    border-radius: 999px;
    padding: 8px 14px;
    font-size: 0.82rem;
    font-weight: 700;
}

.dot-green {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 100%;
    display: inline-block;
}

/* KPI */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 18px;
    height: 150px;
    min-height: 150px;
    max-height: 150px;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04);
    box-sizing: border-box;
    overflow: hidden;
}

.kpi-card-blue {
    background: #eff6ff;
    border-color: #bfdbfe;
}

.kpi-card-red {
    background: #fef2f2;
    border-color: #fecaca;
}

.kpi-card-yellow {
    background: #fffbeb;
    border-color: #fde68a;
}

.kpi-card-green {
    background: #ecfdf5;
    border-color: #a7f3d0;
}

.kpi-label {
    color: #64748b;
    font-size: 0.72rem;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
}


.kpi-value {
    color: #0f172a;
    font-size: 1.55rem;
    font-weight: 850;
    line-height: 1.12;
}

.kpi-help {
    color: #64748b;
    font-size: 0.82rem;
    margin-top: 8px;
    line-height: 1.35;
}

/* Cards */
.custom-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04);
    margin-bottom: 16px;
    box-sizing: border-box;
}
                
.equal-card {
    min-height: 430px;
}

.card-title {
    font-size: 1.05rem;
    font-weight: 850;
    color: #0f172a;
    margin-bottom: 8px;
}


.card-title-large {
    font-size: 1.35rem;
    font-weight: 850;
    color: #111827;
    margin-bottom: 8px;
}

.card-subtitle {
    color: #64748b;
    font-size: 0.88rem;
    margin-bottom: 10px;
}
                
/* Tarjetas de contenido: fondo uniforme */
.content-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04);
    min-height: 330px;
}

/* Tarjeta ancha para regulación */
.content-card-wide {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04);
}


/* Barras tipo Bolt */
.progress-row {
    margin-bottom: 18px;
}
                
.progress-row:last-child {
    margin-bottom: 6px;
}                


.progress-track {
    width: 100%;
    height: 11px;
    background: #e5e7eb;
    border-radius: 999px;
    overflow: hidden;
}

.progress-fill {
    height: 11px;
    background: #2563eb;
    border-radius: 999px;
}


/* Evita que Plotly deje bloques blancos grandes */
.js-plotly-plot,
.plotly,
.plot-container,
.svg-container {
    background: #ffffff !important;
}                


.hypothesis-box {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 14px;
    padding: 16px 18px;
    font-weight: 750;
    line-height: 1.48;
    white-space: normal;
    font-size: 0.92rem;
}
                

.method-grid {
    display: grid;
    grid-template-columns: 1fr 1.35fr 1.2fr;
    gap: 18px;
    align-items: stretch;
    margin-top: 14px;
}                               
                

            
.method-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 16px 17px;
    min-height: 142px;
    height: 142px;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.035);
    box-sizing: border-box;
    overflow: hidden;
}                              

 
.method-title {
    font-size: 0.88rem;
    font-weight: 850;
    color: #334155;
    margin-bottom: 12px;
    line-height: 1.22;
}                              

.method-text {
    font-size: 0.80rem;
    color: #64748b;
    line-height: 1.35;
    word-break: normal;
    overflow-wrap: normal;
}              


/* Reduce espacios verticales */
div[data-testid="stVerticalBlock"] {
    gap: 0.55rem;
}


/* Títulos de tarjetas */
.section-title-card {
    font-size: 1.25rem;
    font-weight: 850;
    color: #111827;
    margin-bottom: 6px;
}

.section-subtitle-card {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 14px;
}

/* Mensaje vacío */
.empty-state {
    background: #fffbeb;
    color: #a16207;
    border: 1px solid #fde68a;
    border-radius: 14px;
    padding: 14px 16px;
    font-size: 0.92rem;
    line-height: 1.4;
}



.progress-row-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #334155;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 8px;
}


/* =========================================================
   Tarjetas blancas para contenedores con key
   ========================================================= */

.st-key-card_perfil,
.st-key-card_aceptacion,
.st-key-card_confianza,
.st-key-card_regulacion {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 14px !important;
    padding: 18px 18px 18px 18px !important;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04) !important;
    overflow: hidden !important;
}

/* Fuerza blanco en todo el contenido interno de esas tarjetas */
.st-key-card_perfil *,
.st-key-card_aceptacion *,
.st-key-card_confianza *,
.st-key-card_regulacion * {
    background-color: transparent !important;
}

/* Pero los bloques principales sí deben quedar blancos */
.st-key-card_perfil,
.st-key-card_perfil > div,
.st-key-card_perfil [data-testid="stVerticalBlock"],
.st-key-card_perfil [data-testid="stElementContainer"],
.st-key-card_perfil [data-testid="stPlotlyChart"],
.st-key-card_aceptacion,
.st-key-card_aceptacion > div,
.st-key-card_aceptacion [data-testid="stVerticalBlock"],
.st-key-card_aceptacion [data-testid="stElementContainer"],
.st-key-card_aceptacion [data-testid="stPlotlyChart"],
.st-key-card_confianza,
.st-key-card_confianza > div,
.st-key-card_confianza [data-testid="stVerticalBlock"],
.st-key-card_confianza [data-testid="stElementContainer"],
.st-key-card_confianza [data-testid="stPlotlyChart"],
.st-key-card_regulacion,
.st-key-card_regulacion > div,
.st-key-card_regulacion [data-testid="stVerticalBlock"],
.st-key-card_regulacion [data-testid="stElementContainer"],
.st-key-card_regulacion [data-testid="stMarkdownContainer"] {
    background-color: #ffffff !important;
}

/* Plotly blanco real */
.st-key-card_perfil .js-plotly-plot,
.st-key-card_perfil .plotly,
.st-key-card_perfil .plot-container,
.st-key-card_perfil .svg-container,
.st-key-card_aceptacion .js-plotly-plot,
.st-key-card_aceptacion .plotly,
.st-key-card_aceptacion .plot-container,
.st-key-card_aceptacion .svg-container,
.st-key-card_confianza .js-plotly-plot,
.st-key-card_confianza .plotly,
.st-key-card_confianza .plot-container,
.st-key-card_confianza .svg-container {
    background: #ffffff !important;
}

/* Mantener colores de alertas, no volverlas transparentes */
.st-key-card_aceptacion .alert-warning {
    background: #fffbeb !important;
}

.st-key-card_confianza .alert-danger {
    background: #fff7ed !important;
}

/* Mantener barras de regulación */
.st-key-card_regulacion .progress-track {
    background: #e5e7eb !important;
}

.st-key-card_regulacion .progress-fill {
    background: #2563eb !important;
}

/* Espacio inferior para tarjetas con gráficos y alertas */
.alert-warning {
    background: #fffbeb;
    border: 1px solid #fde68a;
    color: #b45309;
    border-radius: 14px;
    padding: 12px 14px;
    font-size: 0.88rem;
    line-height: 1.35;
    margin-top: 10px;
    margin-bottom: 14px;
}
                
.alert-danger {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    color: #c2410c;
    border-radius: 14px;
    padding: 12px 14px;
    font-size: 0.88rem;
    line-height: 1.35;
    margin-top: 10px;
    margin-bottom: 14px;
}
                
.section-gap-small {
    height: 1px;
}


/* =========================================================
   Perfil de la muestra
   ========================================================= */

.st-key-card_pm_edad,
.st-key-card_pm_genero,
.st-key-card_pm_rol,
.st-key-card_pm_quito,
.st-key-card_pm_facultad {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 14px !important;
    padding: 18px 18px 16px 18px !important;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04) !important;
    overflow: hidden !important;
}

.st-key-card_pm_edad *,
.st-key-card_pm_genero *,
.st-key-card_pm_rol *,
.st-key-card_pm_quito *,
.st-key-card_pm_facultad * {
    background-color: transparent !important;
}

.st-key-card_pm_edad,
.st-key-card_pm_edad > div,
.st-key-card_pm_edad [data-testid="stVerticalBlock"],
.st-key-card_pm_edad [data-testid="stElementContainer"],
.st-key-card_pm_edad [data-testid="stPlotlyChart"],
.st-key-card_pm_genero,
.st-key-card_pm_genero > div,
.st-key-card_pm_genero [data-testid="stVerticalBlock"],
.st-key-card_pm_genero [data-testid="stElementContainer"],
.st-key-card_pm_genero [data-testid="stPlotlyChart"],
.st-key-card_pm_rol,
.st-key-card_pm_rol > div,
.st-key-card_pm_rol [data-testid="stVerticalBlock"],
.st-key-card_pm_rol [data-testid="stElementContainer"],
.st-key-card_pm_rol [data-testid="stPlotlyChart"],
.st-key-card_pm_quito,
.st-key-card_pm_quito > div,
.st-key-card_pm_quito [data-testid="stVerticalBlock"],
.st-key-card_pm_quito [data-testid="stElementContainer"],
.st-key-card_pm_quito [data-testid="stPlotlyChart"],
.st-key-card_pm_facultad,
.st-key-card_pm_facultad > div,
.st-key-card_pm_facultad [data-testid="stVerticalBlock"],
.st-key-card_pm_facultad [data-testid="stElementContainer"],
.st-key-card_pm_facultad [data-testid="stPlotlyChart"] {
    background-color: #ffffff !important;
}

.st-key-card_pm_edad .js-plotly-plot,
.st-key-card_pm_edad .plotly,
.st-key-card_pm_edad .plot-container,
.st-key-card_pm_edad .svg-container,
.st-key-card_pm_genero .js-plotly-plot,
.st-key-card_pm_genero .plotly,
.st-key-card_pm_genero .plot-container,
.st-key-card_pm_genero .svg-container,
.st-key-card_pm_rol .js-plotly-plot,
.st-key-card_pm_rol .plotly,
.st-key-card_pm_rol .plot-container,
.st-key-card_pm_rol .svg-container,
.st-key-card_pm_quito .js-plotly-plot,
.st-key-card_pm_quito .plotly,
.st-key-card_pm_quito .plot-container,
.st-key-card_pm_quito .svg-container,
.st-key-card_pm_facultad .js-plotly-plot,
.st-key-card_pm_facultad .plotly,
.st-key-card_pm_facultad .plot-container,
.st-key-card_pm_facultad .svg-container {
    background: #ffffff !important;
}
                
.profile-section-gap {
    height: 24px;
}   


.profile-card-header-soft {
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%) !important;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 10px 12px;
    margin-bottom: 8px;
}                

.profile-card-header-soft .section-title-card {
    margin-bottom: 4px;
}

.profile-card-header-soft .section-subtitle-card {
    margin-bottom: 0;
}                                             

/* =========================================================
   Conocimiento de IA
   ========================================================= */

.st-key-card_ia_escucho,
.st-key-card_ia_reconocio,
.st-key-card_ia_identifica,
.st-key-card_ia_falso,
.st-key-card_ia_interpretacion {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 16px !important;
    padding: 20px 20px 18px 20px !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    overflow: hidden !important;
}

.st-key-card_ia_escucho *,
.st-key-card_ia_reconocio *,
.st-key-card_ia_identifica *,
.st-key-card_ia_falso *,
.st-key-card_ia_interpretacion * {
    background-color: transparent !important;
}

.st-key-card_ia_escucho,
.st-key-card_ia_escucho > div,
.st-key-card_ia_escucho [data-testid="stVerticalBlock"],
.st-key-card_ia_escucho [data-testid="stElementContainer"],
.st-key-card_ia_escucho [data-testid="stPlotlyChart"],
.st-key-card_ia_reconocio,
.st-key-card_ia_reconocio > div,
.st-key-card_ia_reconocio [data-testid="stVerticalBlock"],
.st-key-card_ia_reconocio [data-testid="stElementContainer"],
.st-key-card_ia_reconocio [data-testid="stPlotlyChart"],
.st-key-card_ia_identifica,
.st-key-card_ia_identifica > div,
.st-key-card_ia_identifica [data-testid="stVerticalBlock"],
.st-key-card_ia_identifica [data-testid="stElementContainer"],
.st-key-card_ia_identifica [data-testid="stPlotlyChart"],
.st-key-card_ia_falso,
.st-key-card_ia_falso > div,
.st-key-card_ia_falso [data-testid="stVerticalBlock"],
.st-key-card_ia_falso [data-testid="stElementContainer"],
.st-key-card_ia_falso [data-testid="stPlotlyChart"],
.st-key-card_ia_interpretacion,
.st-key-card_ia_interpretacion > div,
.st-key-card_ia_interpretacion [data-testid="stVerticalBlock"],
.st-key-card_ia_interpretacion [data-testid="stElementContainer"],
.st-key-card_ia_interpretacion [data-testid="stMarkdownContainer"] {
    background-color: #ffffff !important;
}

.st-key-card_ia_escucho .js-plotly-plot,
.st-key-card_ia_escucho .plotly,
.st-key-card_ia_escucho .plot-container,
.st-key-card_ia_escucho .svg-container,
.st-key-card_ia_reconocio .js-plotly-plot,
.st-key-card_ia_reconocio .plotly,
.st-key-card_ia_reconocio .plot-container,
.st-key-card_ia_reconocio .svg-container,
.st-key-card_ia_identifica .js-plotly-plot,
.st-key-card_ia_identifica .plotly,
.st-key-card_ia_identifica .plot-container,
.st-key-card_ia_identifica .svg-container,
.st-key-card_ia_falso .js-plotly-plot,
.st-key-card_ia_falso .plotly,
.st-key-card_ia_falso .plot-container,
.st-key-card_ia_falso .svg-container {
    background: #ffffff !important;
}

.interpretation-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-top: 12px;
}

.interpretation-box {
    border-radius: 14px;
    padding: 16px;
    border: 1px solid #e5e7eb;
}

.interpretation-box.blue {
    background: #eff6ff !important;
    border-color: #bfdbfe;
}

.interpretation-box.green {
    background: #ecfdf5 !important;
    border-color: #a7f3d0;
}

.interpretation-box.yellow {
    background: #fffbeb !important;
    border-color: #fde68a;
}

.interpretation-box.red {
    background: #fff1f2 !important;
    border-color: #fecdd3;
}

.interpretation-value {
    font-size: 1.55rem;
    font-weight: 850;
    color: #0f172a;
    line-height: 1.1;
    margin-bottom: 8px;
}

.interpretation-label {
    color: #64748b;
    font-size: 0.84rem;
    line-height: 1.35;
}

                
/* =========================================================
   Percepción ciudadana
   ========================================================= */

.analysis-subsection-header {
    margin-top: 1.05rem;
    margin-bottom: 0.6rem;
}

.analysis-subsection-title {
    font-size: clamp(1.05rem, 1.8vw, 1.28rem);
    font-weight: 850;
    color: #111827;
    letter-spacing: -0.02em;
    line-height: 1.25;
}

.analysis-subsection-desc {
    margin-top: 0.25rem;
    font-size: clamp(0.82rem, 1.3vw, 0.94rem);
    color: #64748b;
    line-height: 1.45;
    max-width: 1100px;
}

.analysis-note-compact,
.analysis-note-compact-green,
.analysis-note-compact-yellow,
.analysis-note-compact-red {
    border-radius: 14px;
    padding: 0.78rem 0.95rem;
    font-size: clamp(0.82rem, 1.2vw, 0.9rem);
    line-height: 1.45;
    margin-top: 0.45rem;
    margin-bottom: 0.85rem;
    width: 100%;
    box-sizing: border-box;
    overflow-wrap: break-word;
}

.analysis-note-compact {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}

.analysis-note-compact-green {
    background: #ecfdf5 !important;
    border: 1px solid #a7f3d0;
    color: #047857;
}

.analysis-note-compact-yellow {
    background: #fffbeb !important;
    border: 1px solid #fde68a;
    color: #b45309;
}

.analysis-note-compact-red {
    background: #fff7ed !important;
    border: 1px solid #fed7aa;
    color: #c2410c;
}

.st-key-card_pc_matriz,
.st-key-card_pc_aceptacion,
.st-key-card_pc_manipulacion,
.st-key-card_pc_desconfianza,
.st-key-card_pc_regulacion,
.st-key-card_pc_interpretacion,
.st-key-card_pc_edad_riesgo {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 18px !important;
    padding: clamp(18px, 2.2vw, 28px) !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    overflow: hidden !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.st-key-card_pc_matriz *,
.st-key-card_pc_aceptacion *,
.st-key-card_pc_manipulacion *,
.st-key-card_pc_desconfianza *,
.st-key-card_pc_regulacion *,
.st-key-card_pc_interpretacion *,
.st-key-card_pc_edad_riesgo * {
    background-color: transparent !important;
}

.st-key-card_pc_matriz,
.st-key-card_pc_matriz > div,
.st-key-card_pc_matriz [data-testid="stVerticalBlock"],
.st-key-card_pc_matriz [data-testid="stElementContainer"],
.st-key-card_pc_matriz [data-testid="stPlotlyChart"],
.st-key-card_pc_aceptacion,
.st-key-card_pc_aceptacion > div,
.st-key-card_pc_aceptacion [data-testid="stVerticalBlock"],
.st-key-card_pc_aceptacion [data-testid="stElementContainer"],
.st-key-card_pc_aceptacion [data-testid="stPlotlyChart"],
.st-key-card_pc_manipulacion,
.st-key-card_pc_manipulacion > div,
.st-key-card_pc_manipulacion [data-testid="stVerticalBlock"],
.st-key-card_pc_manipulacion [data-testid="stElementContainer"],
.st-key-card_pc_manipulacion [data-testid="stPlotlyChart"],
.st-key-card_pc_desconfianza,
.st-key-card_pc_desconfianza > div,
.st-key-card_pc_desconfianza [data-testid="stVerticalBlock"],
.st-key-card_pc_desconfianza [data-testid="stElementContainer"],
.st-key-card_pc_desconfianza [data-testid="stPlotlyChart"],
.st-key-card_pc_regulacion,
.st-key-card_pc_regulacion > div,
.st-key-card_pc_regulacion [data-testid="stVerticalBlock"],
.st-key-card_pc_regulacion [data-testid="stElementContainer"],
.st-key-card_pc_regulacion [data-testid="stPlotlyChart"],
.st-key-card_pc_interpretacion,
.st-key-card_pc_interpretacion > div,
.st-key-card_pc_interpretacion [data-testid="stVerticalBlock"],
.st-key-card_pc_interpretacion [data-testid="stElementContainer"],
.st-key-card_pc_interpretacion [data-testid="stMarkdownContainer"],
.st-key-card_pc_edad_riesgo,
.st-key-card_pc_edad_riesgo > div,
.st-key-card_pc_edad_riesgo [data-testid="stVerticalBlock"],
.st-key-card_pc_edad_riesgo [data-testid="stElementContainer"],
.st-key-card_pc_edad_riesgo [data-testid="stPlotlyChart"],
.st-key-card_pc_edad_riesgo [data-testid="stMarkdownContainer"] {
    background-color: #ffffff !important;
}

.st-key-card_pc_matriz .js-plotly-plot,
.st-key-card_pc_aceptacion .js-plotly-plot,
.st-key-card_pc_manipulacion .js-plotly-plot,
.st-key-card_pc_desconfianza .js-plotly-plot,
.st-key-card_pc_regulacion .js-plotly-plot,
.st-key-card_pc_edad_riesgo .js-plotly-plot,
.st-key-card_pc_matriz .plotly,
.st-key-card_pc_aceptacion .plotly,
.st-key-card_pc_manipulacion .plotly,
.st-key-card_pc_desconfianza .plotly,
.st-key-card_pc_regulacion .plotly,
.st-key-card_pc_edad_riesgo .plotly,
.st-key-card_pc_matriz .plot-container,
.st-key-card_pc_aceptacion .plot-container,
.st-key-card_pc_manipulacion .plot-container,
.st-key-card_pc_desconfianza .plot-container,
.st-key-card_pc_regulacion .plot-container,
.st-key-card_pc_edad_riesgo .plot-container,
.st-key-card_pc_matriz .svg-container,
.st-key-card_pc_aceptacion .svg-container,
.st-key-card_pc_manipulacion .svg-container,
.st-key-card_pc_desconfianza .svg-container,
.st-key-card_pc_regulacion .svg-container,
.st-key-card_pc_edad_riesgo .svg-container {
    background: #ffffff !important;
}


.st-key-card_pc_aceptacion,
.st-key-card_pc_manipulacion,
.st-key-card_pc_desconfianza,
.st-key-card_pc_regulacion {
    min-height: 0 !important;
    height: auto !important;
    max-height: none !important;
    padding: 14px 16px 16px 16px !important;
    display: block !important;
}

.st-key-card_pc_interpretacion .interpretation-grid {
    margin-top: 18px;
    gap: 14px;
}

.st-key-card_pc_interpretacion .interpretation-box {
    min-height: 125px;
    padding: 18px 18px;
}

.interpretation-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-top: 12px;
}

.interpretation-box {
    border-radius: 14px;
    padding: 16px;
    border: 1px solid #e5e7eb;
    box-sizing: border-box;
    overflow-wrap: break-word;
}

.interpretation-box.blue {
    background: #eff6ff !important;
    border-color: #bfdbfe;
}

.interpretation-box.green {
    background: #ecfdf5 !important;
    border-color: #a7f3d0;
}

.interpretation-box.yellow {
    background: #fffbeb !important;
    border-color: #fde68a;
}

.interpretation-box.red {
    background: #fff7ed !important;
    border-color: #fed7aa;
}

.interpretation-value {
    font-size: clamp(1.35remfed7aa;
}

, 2.2vw, 1.65rem);
    font-weight: 900;
    color: #0f172a;
    line-height: 1.1;
    margin-bottom: 8px;
}

.interpretation-label {
    color: #64748b;
    font-size: clamp(0.78rem, 1.1vw, 0.86rem);
    line-height: 1.38;
}

            
.alert-info-blue,
.alert-info-green,
.alert-warning,
.alert-danger {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow-wrap: break-word !important;
    border-radius: 12px;
    padding: 10px 12px;
    font-size: clamp(0.78rem, 1.1vw, 0.86rem);
    line-height: 1.32;
    margin-top: 6px;
    margin-bottom: 8px;
}                

.alert-info-blue {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}

.alert-info-green {
    background: #ecfdf5 !important;
    border: 1px solid #a7f3d0;
    color: #047857;
}

.alert-warning {
    background: #fffbeb !important;
    border: 1px solid #fde68a;
    color: #b45309;
}

.alert-danger {
    background: #fff7ed !important;
    border: 1px solid #fed7aa;
    color: #c2410c;
}

.section-gap-xs {
    height: 10px !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stElementContainer"]:has(.section-gap-xs) {
    margin: 0 !important;
    padding: 0 !important;
    height: 10px !important;
}

/* Tabs más limpias */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #e5e7eb;
}

.stTabs [data-baseweb="tab"] {
    padding: 10px 14px;
    color: #334155;
    font-size: 0.92rem;
}

.stTabs [aria-selected="true"] {
    color: #ef4444 !important;
    font-weight: 800;
}

/* Responsive percepción ciudadana */
@media (max-width: 1100px) {
    .interpretation-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .st-key-card_pc_aceptacion,
    .st-key-card_pc_manipulacion,
    .st-key-card_pc_desconfianza,
    .st-key-card_pc_regulacion {
        min-height: auto !important;
    }
}

@media (max-width: 760px) {
    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    .profile-card-header-soft {
        padding: 10px 12px !important;
    }

    .section-title-card {
        font-size: 1.02rem !important;
        line-height: 1.25 !important;
    }

    .section-subtitle-card {
        font-size: 0.8rem !important;
        line-height: 1.35 !important;
    }

    .interpretation-grid {
        grid-template-columns: 1fr;
        gap: 10px;
    }

    .interpretation-box {
        min-height: auto !important;
        padding: 14px 14px !important;
    }

    .analysis-subsection-header {
        margin-top: 0.8rem;
        margin-bottom: 0.5rem;
    }

    .analysis-note-compact,
    .analysis-note-compact-green,
    .analysis-note-compact-yellow,
    .analysis-note-compact-red {
        padding: 0.72rem 0.85rem;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 8px 10px;
        font-size: 0.84rem;
    }
}

@media (max-width: 520px) {
    .topbar {
        padding: 14px 16px !important;
    }

    .topbar-title {
        font-size: 1.2rem !important;
    }

    .topbar-subtitle {
        font-size: 0.82rem !important;
    }

    .topbar-pill {
        position: static !important;
        margin-top: 10px;
    }

    .small-pill {
        font-size: 0.76rem !important;
        padding: 7px 10px !important;
    }

    .kpi-card {
        height: auto !important;
        min-height: 118px !important;
        max-height: none !important;
        padding: 14px !important;
    }

    .kpi-value {
        font-size: 1.35rem !important;
    }

    .kpi-help {
        font-size: 0.78rem !important;
    }
} 

/* =========================================================
   Compactación responsive de tarjetas de percepción
   ========================================================= */

@media (min-width: 900px) {
    .st-key-card_pc_aceptacion,
    .st-key-card_pc_manipulacion,
    .st-key-card_pc_desconfianza,
    .st-key-card_pc_regulacion {
        min-height: 360px !important;
        padding: 16px 16px 18px 16px !important;
    }
}

@media (max-width: 899px) {
    .st-key-card_pc_aceptacion,
    .st-key-card_pc_manipulacion,
    .st-key-card_pc_desconfianza,
    .st-key-card_pc_regulacion {
        min-height: auto !important;
        padding: 14px !important;
    }

    .profile-card-header-soft {
        padding: 9px 10px !important;
        margin-bottom: 8px !important;
    }
}                               
                

/* =========================================================
   Confianza electoral
   ========================================================= */

.st-key-card_ce_matriz,
.st-key-card_ce_limpieza,
.st-key-card_ce_fraude,
.st-key-card_ce_influencia_voto,
.st-key-card_ce_cambio_confianza,
.st-key-card_ce_indice,
.st-key-card_ce_interpretacion {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 16px !important;
    padding: 28px 28px 34px 28px !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    overflow: hidden !important;
}

.st-key-card_ce_matriz *,
.st-key-card_ce_limpieza *,
.st-key-card_ce_fraude *,
.st-key-card_ce_influencia_voto *,
.st-key-card_ce_cambio_confianza *,
.st-key-card_ce_indice *,
.st-key-card_ce_interpretacion * {
    background-color: transparent !important;
}

.st-key-card_ce_matriz,
.st-key-card_ce_matriz > div,
.st-key-card_ce_matriz [data-testid="stVerticalBlock"],
.st-key-card_ce_matriz [data-testid="stElementContainer"],
.st-key-card_ce_matriz [data-testid="stPlotlyChart"],
.st-key-card_ce_limpieza,
.st-key-card_ce_limpieza > div,
.st-key-card_ce_limpieza [data-testid="stVerticalBlock"],
.st-key-card_ce_limpieza [data-testid="stElementContainer"],
.st-key-card_ce_limpieza [data-testid="stPlotlyChart"],
.st-key-card_ce_fraude,
.st-key-card_ce_fraude > div,
.st-key-card_ce_fraude [data-testid="stVerticalBlock"],
.st-key-card_ce_fraude [data-testid="stElementContainer"],
.st-key-card_ce_fraude [data-testid="stPlotlyChart"],
.st-key-card_ce_influencia_voto,
.st-key-card_ce_influencia_voto > div,
.st-key-card_ce_influencia_voto [data-testid="stVerticalBlock"],
.st-key-card_ce_influencia_voto [data-testid="stElementContainer"],
.st-key-card_ce_influencia_voto [data-testid="stPlotlyChart"],
.st-key-card_ce_cambio_confianza,
.st-key-card_ce_cambio_confianza > div,
.st-key-card_ce_cambio_confianza [data-testid="stVerticalBlock"],
.st-key-card_ce_cambio_confianza [data-testid="stElementContainer"],
.st-key-card_ce_cambio_confianza [data-testid="stPlotlyChart"],
.st-key-card_ce_indice,
.st-key-card_ce_indice > div,
.st-key-card_ce_indice [data-testid="stVerticalBlock"],
.st-key-card_ce_indice [data-testid="stElementContainer"],
.st-key-card_ce_indice [data-testid="stPlotlyChart"],
.st-key-card_ce_interpretacion,
.st-key-card_ce_interpretacion > div,
.st-key-card_ce_interpretacion [data-testid="stVerticalBlock"],
.st-key-card_ce_interpretacion [data-testid="stElementContainer"],
.st-key-card_ce_interpretacion [data-testid="stMarkdownContainer"] {
    background-color: #ffffff !important;
}

.st-key-card_ce_matriz .js-plotly-plot,
.st-key-card_ce_limpieza .js-plotly-plot,
.st-key-card_ce_fraude .js-plotly-plot,
.st-key-card_ce_influencia_voto .js-plotly-plot,
.st-key-card_ce_cambio_confianza .js-plotly-plot,
.st-key-card_ce_indice .js-plotly-plot,
.st-key-card_ce_matriz .plotly,
.st-key-card_ce_limpieza .plotly,
.st-key-card_ce_fraude .plotly,
.st-key-card_ce_influencia_voto .plotly,
.st-key-card_ce_cambio_confianza .plotly,
.st-key-card_ce_indice .plotly,
.st-key-card_ce_matriz .plot-container,
.st-key-card_ce_limpieza .plot-container,
.st-key-card_ce_fraude .plot-container,
.st-key-card_ce_influencia_voto .plot-container,
.st-key-card_ce_cambio_confianza .plot-container,
.st-key-card_ce_indice .plot-container,
.st-key-card_ce_matriz .svg-container,
.st-key-card_ce_limpieza .svg-container,
.st-key-card_ce_fraude .svg-container,
.st-key-card_ce_influencia_voto .svg-container,
.st-key-card_ce_cambio_confianza .svg-container,
.st-key-card_ce_indice .svg-container {
    background: #ffffff !important;
}

.st-key-card_ce_limpieza,
.st-key-card_ce_fraude,
.st-key-card_ce_influencia_voto,
.st-key-card_ce_cambio_confianza {
    min-height: 430px !important;
    height: 430px !important;
    padding: 20px 20px 24px 20px !important;
    display: flex !important;
    flex-direction: column !important;
}

.st-key-card_ce_limpieza .alert-info-blue,
.st-key-card_ce_fraude .alert-danger,
.st-key-card_ce_influencia_voto .alert-warning,
.st-key-card_ce_cambio_confianza .alert-info-green {
    margin-top: auto !important;
}

.ce-section-gap {
    height: 8px !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stElementContainer"]:has(.ce-section-gap) {
    margin: 0 !important;
    padding: 0 !important;
    height: 8px !important;
}

.st-key-card_ce_interpretacion .interpretation-grid {
    margin-top: 24px;
    gap: 18px;
}

.st-key-card_ce_interpretacion .interpretation-box {
    min-height: 145px;
    padding: 22px 20px;
}

/* =========================================================
   Modelos predictivos
   ========================================================= */

.st-key-card_mp_metricas,
.st-key-card_mp_importancia,
.st-key-card_mp_estabilidad,
.st-key-card_mp_clases,
.st-key-card_mp_justificacion,
.st-key-card_mp_interpretacion {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 16px !important;
    padding: 26px 28px 30px 28px !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    overflow: hidden !important;
}

.st-key-card_mp_metricas *,
.st-key-card_mp_importancia *,
.st-key-card_mp_estabilidad *,
.st-key-card_mp_clases *,
.st-key-card_mp_justificacion *,
.st-key-card_mp_interpretacion * {
    background-color: transparent !important;
}

.st-key-card_mp_metricas,
.st-key-card_mp_metricas > div,
.st-key-card_mp_metricas [data-testid="stVerticalBlock"],
.st-key-card_mp_metricas [data-testid="stElementContainer"],
.st-key-card_mp_importancia,
.st-key-card_mp_importancia > div,
.st-key-card_mp_importancia [data-testid="stVerticalBlock"],
.st-key-card_mp_importancia [data-testid="stElementContainer"],
.st-key-card_mp_estabilidad,
.st-key-card_mp_estabilidad > div,
.st-key-card_mp_estabilidad [data-testid="stVerticalBlock"],
.st-key-card_mp_estabilidad [data-testid="stElementContainer"],
.st-key-card_mp_clases,
.st-key-card_mp_clases > div,
.st-key-card_mp_clases [data-testid="stVerticalBlock"],
.st-key-card_mp_clases [data-testid="stElementContainer"],
.st-key-card_mp_justificacion,
.st-key-card_mp_justificacion > div,
.st-key-card_mp_justificacion [data-testid="stVerticalBlock"],
.st-key-card_mp_justificacion [data-testid="stElementContainer"],
.st-key-card_mp_interpretacion,
.st-key-card_mp_interpretacion > div,
.st-key-card_mp_interpretacion [data-testid="stVerticalBlock"],
.st-key-card_mp_interpretacion [data-testid="stElementContainer"],
.st-key-card_mp_interpretacion [data-testid="stMarkdownContainer"] {
    background-color: #ffffff !important;
}

.mp-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 22px;
}

.mp-kpi {
    border-radius: 16px;
    padding: 18px 20px;
    min-height: 130px;
    border: 1px solid #e5e7eb;
    box-sizing: border-box;
}

.mp-kpi.teal {
    background: #f0fdfa !important;
    border-color: #99f6e4;
}

.mp-kpi.blue {
    background: #eff6ff !important;
    border-color: #bfdbfe;
}

.mp-kpi.green {
    background: #ecfdf5 !important;
    border-color: #a7f3d0;
}

.mp-kpi.yellow {
    background: #fffbeb !important;
    border-color: #fde68a;
}

.mp-kpi-label {
    font-size: 0.72rem;
    font-weight: 850;
    color: #64748b;
    text-transform: uppercase;
    line-height: 1.2;
    margin-bottom: 8px;
}

.mp-kpi-value {
    font-size: 1.65rem;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.05;
}

.mp-selected {
    font-size: 1.42rem;
    font-weight: 900;
    color: #0f766e;
    line-height: 1.05;
}

.mp-kpi-help {
    color: #64748b;
    font-size: 0.82rem;
    margin-top: 8px;
    line-height: 1.3;
}

.mp-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
}

.mp-table th {
    text-align: left;
    color: #64748b;
    font-size: 0.72rem;
    text-transform: uppercase;
    padding: 12px 10px;
    border-bottom: 1px solid #e5e7eb;
}

.mp-table td {
    padding: 14px 10px;
    border-bottom: 1px solid #eef2f7;
    color: #334155;
    font-weight: 650;
}

.mp-table tr.selected {
    background: #ecfdf5 !important;
}

.mp-pill {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 0.74rem;
    font-weight: 850;
}

.mp-pill.green {
    background: #dcfce7 !important;
    color: #15803d;
}

.mp-pill.yellow {
    background: #fef3c7 !important;
    color: #b45309;
}

.mp-pill.red {
    background: #fee2e2 !important;
    color: #b91c1c;
}

.mp-note-green {
    background: #ecfdf5 !important;
    border: 1px solid #a7f3d0;
    border-radius: 14px;
    padding: 16px 18px;
    color: #047857;
    font-size: 0.9rem;
    line-height: 1.45;
    margin-top: 18px;
}

.mp-note-blue {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe;
    border-radius: 14px;
    padding: 16px 18px;
    color: #1d4ed8;
    font-size: 0.9rem;
    line-height: 1.45;
    margin-top: 18px;
}

.mp-bar-row {
    margin-bottom: 15px;
}

.mp-bar-head {
    display: flex;
    justify-content: space-between;
    font-size: 0.88rem;
    font-weight: 800;
    color: #334155;
    margin-bottom: 6px;
}

.mp-track {
    width: 100%;
    height: 10px;
    background: #eef2f7 !important;
    border-radius: 999px;
    overflow: hidden;
}

.mp-fill {
    height: 10px;
    background: #0f9f8f !important;
    border-radius: 999px;
}

.mp-seed {
    margin-bottom: 16px;
}

.mp-seed-title {
    font-size: 0.92rem;
    font-weight: 850;
    color: #334155;
    margin-bottom: 7px;
}

.mp-seed-line {
    display: grid;
    grid-template-columns: 64px 1fr 52px;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
    font-size: 0.78rem;
    color: #64748b;
}

.mp-mini-track {
    height: 15px;
    background: #eef2f7 !important;
    border-radius: 999px;
    overflow: hidden;
}

.mp-mini-fill.acc {
    background: #0f9f8f !important;
    height: 15px;
}

.mp-mini-fill.auc {
    background: #2563eb !important;
    height: 15px;
}

.mp-model-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
}

.mp-model-card {
    border-radius: 16px;
    padding: 18px;
    border: 1px solid #e5e7eb;
    min-height: 190px;
}

.mp-model-card.blue {
    background: #eff6ff !important;
    border-color: #bfdbfe;
}

.mp-model-card.green {
    background: #ecfdf5 !important;
    border-color: #a7f3d0;
}

.mp-model-card.yellow {
    background: #fffbeb !important;
    border-color: #fde68a;
}

.mp-model-title {
    font-size: 0.88rem;
    font-weight: 900;
    margin-bottom: 12px;
    color: #0f172a;
}

.mp-model-text {
    color: #64748b;
    font-size: 0.83rem;
    line-height: 1.45;
    margin-bottom: 14px;
}

.mp-badge-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.mp-badge {
    border-radius: 999px;
    padding: 5px 9px;
    font-size: 0.75rem;
    font-weight: 850;
    background: rgba(255,255,255,0.7) !important;
    color: #334155;
}

.mp-section-gap {
    height: 14px !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stElementContainer"]:has(.mp-section-gap) {
    margin: 0 !important;
    padding: 0 !important;
    height: 14px !important;
}

.mp-two-col-equal {
    min-height: 520px;
}

/* =========================================================
   Evidencia digital GDELT + Encuesta
   ========================================================= */

.st-key-card_ed_fuentes,
.st-key-card_ed_encuesta_exposicion,
.st-key-card_ed_encuesta_automatizacion,
.st-key-card_ed_encuesta_falso,
.st-key-card_ed_encuesta_verificacion,
.st-key-card_ed_gdelt_timeline,
.st-key-card_ed_gdelt_tono,
.st-key-card_ed_gdelt_fuentes,
.st-key-card_ed_gdelt_keywords,
.st-key-card_ed_triangulacion,
.st-key-card_ed_interpretacion {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 16px !important;
    padding: 26px 28px 30px 28px !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    overflow: hidden !important;
}

.st-key-card_ed_fuentes *,
.st-key-card_ed_encuesta_exposicion *,
.st-key-card_ed_encuesta_automatizacion *,
.st-key-card_ed_encuesta_falso *,
.st-key-card_ed_encuesta_verificacion *,
.st-key-card_ed_gdelt_timeline *,
.st-key-card_ed_gdelt_tono *,
.st-key-card_ed_gdelt_fuentes *,
.st-key-card_ed_gdelt_keywords *,
.st-key-card_ed_triangulacion *,
.st-key-card_ed_interpretacion * {
    background-color: transparent !important;
}

.ed-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 22px;
}

.ed-kpi {
    border-radius: 16px;
    padding: 18px 20px;
    min-height: 130px;
    border: 1px solid #e5e7eb;
    box-sizing: border-box;
}

.ed-kpi.blue {
    background: #eff6ff !important;
    border-color: #bfdbfe;
}

.ed-kpi.green {
    background: #ecfdf5 !important;
    border-color: #a7f3d0;
}

.ed-kpi.yellow {
    background: #fffbeb !important;
    border-color: #fde68a;
}

.ed-kpi.red {
    background: #fff1f2 !important;
    border-color: #fecdd3;
}

.ed-kpi-label {
    font-size: 0.72rem;
    font-weight: 850;
    color: #64748b;
    text-transform: uppercase;
    line-height: 1.2;
    margin-bottom: 8px;
}

.ed-kpi-value {
    font-size: 1.65rem;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.05;
}

.ed-kpi-help {
    color: #64748b;
    font-size: 0.82rem;
    margin-top: 8px;
    line-height: 1.3;
}

.ed-bar-row {
    margin-bottom: 15px;
}

.ed-bar-head {
    display: flex;
    justify-content: space-between;
    font-size: 0.88rem;
    font-weight: 800;
    color: #334155;
    margin-bottom: 6px;
}

.ed-track {
    width: 100%;
    height: 10px;
    background: #eef2f7 !important;
    border-radius: 999px;
    overflow: hidden;
}

.ed-fill {
    height: 10px;
    background: #0f9f8f !important;
    border-radius: 999px;
}

.ed-fill.blue {
    background: #2563eb !important;
}

.ed-fill.green {
    background: #0f9f8f !important;
}

.ed-fill.yellow {
    background: #f59e0b !important;
}

.ed-fill.red {
    background: #fb7185 !important;
}

.ed-note-blue {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe;
    border-radius: 14px;
    padding: 16px 18px;
    color: #1d4ed8;
    font-size: 0.9rem;
    line-height: 1.45;
    margin-top: 18px;
}

.ed-note-green {
    background: #ecfdf5 !important;
    border: 1px solid #a7f3d0;
    border-radius: 14px;
    padding: 16px 18px;
    color: #047857;
    font-size: 0.9rem;
    line-height: 1.45;
    margin-top: 18px;
}

.ed-note-yellow {
    background: #fffbeb !important;
    border: 1px solid #fde68a;
    border-radius: 14px;
    padding: 16px 18px;
    color: #b45309;
    font-size: 0.9rem;
    line-height: 1.45;
    margin-top: 18px;
}

.ed-note-red {
    background: #fff7ed !important;
    border: 1px solid #fed7aa;
    border-radius: 14px;
    padding: 16px 18px;
    color: #c2410c;
    font-size: 0.9rem;
    line-height: 1.45;
    margin-top: 18px;
}

.ed-section-gap {
    height: 14px !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stElementContainer"]:has(.ed-section-gap) {
    margin: 0 !important;
    padding: 0 !important;
    height: 14px !important;
}

.ed-source-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-top: 18px;
}

.ed-source-card {
    border-radius: 16px;
    padding: 18px;
    border: 1px solid #e5e7eb;
    min-height: 150px;
}

.ed-source-card.blue {
    background: #eff6ff !important;
    border-color: #bfdbfe;
}

.ed-source-card.green {
    background: #ecfdf5 !important;
    border-color: #a7f3d0;
}

.ed-source-card.yellow {
    background: #fffbeb !important;
    border-color: #fde68a;
}

.ed-source-title {
    font-size: 0.9rem;
    font-weight: 900;
    color: #0f172a;
    margin-bottom: 10px;
}

.ed-source-text {
    color: #64748b;
    font-size: 0.84rem;
    line-height: 1.45;
}

.ed-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
}

.ed-table th {
    text-align: left;
    color: #64748b;
    font-size: 0.74rem;
    text-transform: uppercase;
    padding: 10px 8px;
    border-bottom: 1px solid #e5e7eb;
}

.ed-table td {
    padding: 12px 8px;
    border-bottom: 1px solid #eef2f7;
    color: #334155;
    font-weight: 650;
}

.ed-pill {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 0.74rem;
    font-weight: 850;
}

.ed-pill.blue {
    background: #dbeafe !important;
    color: #1d4ed8;
}

.ed-pill.green {
    background: #dcfce7 !important;
    color: #15803d;
}

.ed-pill.yellow {
    background: #fef3c7 !important;
    color: #b45309;
}

.ed-pill.red {
    background: #fee2e2 !important;
    color: #b91c1c;
}

/* =========================================================
   FIX LIMPIO STREAMLIT CLOUD
   Mantiene tarjetas cerradas, evita cortes y no altera local
   ========================================================= */

/* Ancho general igual al diseño local */
.block-container {
    max-width: 1320px !important;
    padding-left: 1.4rem !important;
    padding-right: 1.4rem !important;
}

/* Las columnas no deben forzar desbordes */
[data-testid="column"] {
    min-width: 0 !important;
}

/* Plotly siempre dentro del contenedor */
[data-testid="stPlotlyChart"],
[data-testid="stPlotlyChart"] > div,
.js-plotly-plot,
.plot-container,
.svg-container {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

/* Tarjetas: cerradas, pero con espacio interno para no cortar textos */
[class*="st-key-card_"] {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

/* Contenido interno sin ancho mínimo extraño */
[class*="st-key-card_"] > div,
[class*="st-key-card_"] [data-testid="stVerticalBlock"],
[class*="st-key-card_"] [data-testid="stElementContainer"],
[class*="st-key-card_"] [data-testid="stMarkdownContainer"] {
    max-width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
}

/* Barras HTML: dejar margen derecho para que no se corten valores */
.progress-row,
.mp-bar-row,
.ed-bar-row {
    width: 100% !important;
    max-width: 100% !important;
    padding-right: 22px !important;
    box-sizing: border-box !important;
}

.progress-row-header,
.mp-bar-head,
.ed-bar-head {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) auto !important;
    gap: 12px !important;
    align-items: center !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

.progress-row-header span:first-child,
.mp-bar-head span:first-child,
.ed-bar-head span:first-child {
    min-width: 0 !important;
    overflow-wrap: anywhere !important;
}

.progress-row-header span:last-child,
.mp-bar-head span:last-child,
.ed-bar-head span:last-child {
    white-space: nowrap !important;
    text-align: right !important;
}

/* Tracks de barras dentro del margen seguro */
.progress-track,
.mp-track,
.mp-mini-track,
.ed-track {
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

/* Notas dentro de tarjetas, sin salirse */
.alert-warning,
.alert-danger,
.alert-info-blue,
.alert-info-green,
.mp-note-green,
.mp-note-blue,
.ed-note-blue,
.ed-note-green,
.ed-note-yellow,
.ed-note-red {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow-wrap: break-word !important;
}

/* Quitar alturas rígidas que en Cloud cortan contenido */
.st-key-card_pc_aceptacion,
.st-key-card_pc_manipulacion,
.st-key-card_pc_desconfianza,
.st-key-card_pc_regulacion,
.st-key-card_ce_limpieza,
.st-key-card_ce_fraude,
.st-key-card_ce_influencia_voto,
.st-key-card_ce_cambio_confianza {
    height: auto !important;
    min-height: 430px !important;
}

/* Tabla de modelos: evitar desborde horizontal */
.st-key-card_mp_metricas {
    overflow-x: auto !important;
}

.mp-table {
    width: 100% !important;
    table-layout: fixed !important;
    font-size: 0.78rem !important;
}

.mp-table th,
.mp-table td {
    padding: 10px 6px !important;
    overflow-wrap: break-word !important;
}

/* Ajuste suave en pantallas de Cloud/laptop */
@media (max-width: 1250px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .kpi-value,
    .mp-kpi-value,
    .ed-kpi-value {
        font-size: 1.35rem !important;
    }

    .section-title-card {
        font-size: 1.12rem !important;
    }

    .section-subtitle-card {
        font-size: 0.82rem !important;
    }
}
             
</style>
""", unsafe_allow_html=True)
    