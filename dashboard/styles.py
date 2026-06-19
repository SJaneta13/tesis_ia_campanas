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
    border-radius: 16px;
    padding: 13px 15px;
    min-height: 112px;
    height: auto;
    max-height: none;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04);
    box-sizing: border-box;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
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

.kpi-card-purple {
    background: #f5f3ff;
    border-color: #ddd6fe;
}

.kpi-card-cyan {
    background: #ecfeff;
    border-color: #a5f3fc;
}

.kpi-label {
    color: #64748b;
    font-size: 0.68rem;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 5px;
}

.kpi-value {
    color: #0f172a;
    font-size: 1.42rem;
    font-weight: 850;
    line-height: 1.08;
}

.kpi-help {
    color: #64748b;
    font-size: 0.78rem;
    margin-top: 6px;
    line-height: 1.25;
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
    padding: 0.95rem 1.05rem;
    font-weight: 650;
    line-height: 1.5;
    white-space: normal;
    font-size: 0.92rem;
}

.hypothesis-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
}

.hypothesis-box {
    border-radius: 14px;
    padding: 0.95rem 1.05rem;
    font-weight: 650;
    line-height: 1.45;
    white-space: normal;
    font-size: 0.88rem;
}

.hypothesis-box.h1-box {
    background: #eff6ff !important;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}

.hypothesis-box.h2-box {
    background: #f5f3ff !important;
    color: #6d28d9;
    border: 1px solid #ddd6fe;
}

.hypothesis-label {
    font-size: 0.76rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.035em;
    margin-bottom: 6px;
}

.hypothesis-text {
    font-size: 0.86rem;
    line-height: 1.45;
    font-weight: 650;
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
    height: auto;
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


/* Espaciado vertical base de Streamlit */
div[data-testid="stVerticalBlock"] {
    gap: 0.72rem !important;
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
    padding: 18px 20px 20px 20px !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
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
.st-key-card_perfil [data-testid="stPlotlyChart"] {
    overflow: visible !important;
}                
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

/* =========================================================
   Separadores verticales globales del dashboard
   ========================================================= */

.summary-section-gap,
.profile-section-gap,
.ia-section-gap,
.ce-section-gap,
.mp-section-gap,
.ed-section-gap,
.section-gap,
.section-gap-small {
    height: 14px !important;
    min-height: 14px !important;
    max-height: 14px !important;
    margin: 0 !important;
    padding: 0 !important;
    display: block !important;
}

.section-gap-xs {
    height: 8px !important;
    min-height: 8px !important;
    max-height: 8px !important;
    margin: 0 !important;
    padding: 0 !important;
    display: block !important;
}                

div[data-testid="stElementContainer"]:has(.summary-section-gap),
div[data-testid="stElementContainer"]:has(.profile-section-gap),
div[data-testid="stElementContainer"]:has(.ia-section-gap),
div[data-testid="stElementContainer"]:has(.ce-section-gap),
div[data-testid="stElementContainer"]:has(.mp-section-gap),
div[data-testid="stElementContainer"]:has(.ed-section-gap),
div[data-testid="stElementContainer"]:has(.section-gap),
div[data-testid="stElementContainer"]:has(.section-gap-small) {
    height: 14px !important;
    min-height: 14px !important;
    max-height: 14px !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

div[data-testid="stElementContainer"]:has(.section-gap-xs) {
    height: 8px !important;
    min-height: 8px !important;
    max-height: 8px !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}            
       
           

/* =========================================================
   Lectura interpretativa: sistema visual común
   ========================================================= */

[class*="st-key-card_"][class*="_interpretacion"] {
    padding: 22px 24px 26px 24px !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    box-sizing: border-box !important;
}

[class*="st-key-card_"][class*="_interpretacion"] .section-title-card {
    margin-bottom: 6px !important;
}

[class*="st-key-card_"][class*="_interpretacion"] .section-subtitle-card {
    margin-bottom: 16px !important;
    line-height: 1.38 !important;
}

.interpretation-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-top: 0;
    margin-bottom: 4px;
    align-items: stretch;
}

.interpretation-box {
    border-radius: 14px;
    padding: 16px 18px;
    border: 1px solid #e5e7eb;
    box-sizing: border-box;
    overflow-wrap: break-word;
    min-height: 116px;
    display: flex;
    flex-direction: column;
    justify-content: center;
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
    font-size: clamp(1.38rem, 2vw, 1.55rem);
    font-weight: 900;
    color: #0f172a;
    line-height: 1.05;
    margin-bottom: 8px;
}

.interpretation-label {
    color: #64748b;
    font-size: clamp(0.79rem, 1vw, 0.85rem);
    line-height: 1.36;
}  

.method-note,
.ia-method-note,
.analysis-method-note {
    color: #6b7280;
    font-size: 0.84rem;
    line-height: 1.42;
    margin-top: 8px;
    margin-bottom: 0;
    padding: 0 2px;
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
    border-radius: 16px !important;
    padding: 18px 20px 20px 20px !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
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
                

.st-key-card_pm_edad .section-title-card,
.st-key-card_pm_genero .section-title-card,
.st-key-card_pm_rol .section-title-card,
.st-key-card_pm_quito .section-title-card,
.st-key-card_pm_facultad .section-title-card {
    font-size: 1.12rem !important;
    line-height: 1.25 !important;
    margin-bottom: 5px !important;
}

.st-key-card_pm_edad .section-subtitle-card,
.st-key-card_pm_genero .section-subtitle-card,
.st-key-card_pm_rol .section-subtitle-card,
.st-key-card_pm_quito .section-subtitle-card,
.st-key-card_pm_facultad .section-subtitle-card {
    font-size: 0.84rem !important;
    line-height: 1.35 !important;
    margin-bottom: 10px !important;
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
    padding: 18px 20px 20px 20px !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}



.ia-card-header-soft {
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%) !important;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 10px 12px;
    margin-bottom: 8px;
}

.ia-card-header-soft .section-title-card {
    font-size: 1.12rem !important;
    line-height: 1.25 !important;
    margin-bottom: 5px !important;
}

.ia-card-header-soft .section-subtitle-card {
    font-size: 0.84rem !important;
    line-height: 1.35 !important;
    margin-bottom: 0 !important;
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


.ia-method-note {
    color: #6b7280;
    font-size: 0.86rem;
    line-height: 1.45;
    margin-top: 10px;
    margin-bottom: 0;
    padding: 0 2px;
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

    [class*="st-key-card_"][class*="_interpretacion"] {
        padding: 16px !important;
    }

    [class*="st-key-card_"][class*="_interpretacion"] .section-title-card {
        font-size: 1rem !important;
        margin-bottom: 5px !important;
    }

    [class*="st-key-card_"][class*="_interpretacion"] .section-subtitle-card {
        font-size: 0.78rem !important;
        margin-bottom: 10px !important;
        line-height: 1.35 !important;
    }

    .interpretation-grid {
        grid-template-columns: 1fr !important;
        gap: 10px !important;
    }

    .interpretation-box {
        min-height: auto !important;
        padding: 13px 14px !important;
    }

    .interpretation-value {
        font-size: 1.28rem !important;
        margin-bottom: 6px !important;
    }

    .interpretation-label {
        font-size: 0.76rem !important;
        line-height: 1.32 !important;
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
                
    .st-key-card_pm_edad,
    .st-key-card_pm_genero,
    .st-key-card_pm_rol,
    .st-key-card_pm_quito,
    .st-key-card_pm_facultad {
        padding: 15px !important;
        border-radius: 14px !important;
    }

    .st-key-card_pm_edad .section-title-card,
    .st-key-card_pm_genero .section-title-card,
    .st-key-card_pm_rol .section-title-card,
    .st-key-card_pm_quito .section-title-card,
    .st-key-card_pm_facultad .section-title-card {
        font-size: 1rem !important;
    }

    .st-key-card_pm_edad .section-subtitle-card,
    .st-key-card_pm_genero .section-subtitle-card,
    .st-key-card_pm_rol .section-subtitle-card,
    .st-key-card_pm_quito .section-subtitle-card,
    .st-key-card_pm_facultad .section-subtitle-card {
        font-size: 0.78rem !important;
        margin-bottom: 8px !important;
    }
                
    .st-key-card_ia_escucho,
    .st-key-card_ia_reconocio,
    .st-key-card_ia_identifica,
    .st-key-card_ia_falso,
    .st-key-card_ia_interpretacion {
        padding: 15px !important;
        border-radius: 14px !important;
    }

    .ia-card-header-soft {
        padding: 9px 10px !important;
        margin-bottom: 8px !important;
    }

    .ia-card-header-soft .section-title-card {
        font-size: 1rem !important;
    }

    .ia-card-header-soft .section-subtitle-card {
        font-size: 0.78rem !important;
    }

    .summary-section-gap,
    .profile-section-gap,
    .ia-section-gap,
    .ce-section-gap,
    .mp-section-gap,
    .ed-section-gap,
    .section-gap-xs,
    .section-gap-small {
        height: 14px !important;
        min-height: 14px !important;
        max-height: 14px !important;
    }

    div[data-testid="stElementContainer"]:has(.summary-section-gap),
    div[data-testid="stElementContainer"]:has(.profile-section-gap),
    div[data-testid="stElementContainer"]:has(.ia-section-gap),
    div[data-testid="stElementContainer"]:has(.ce-section-gap),
    div[data-testid="stElementContainer"]:has(.mp-section-gap),
    div[data-testid="stElementContainer"]:has(.ed-section-gap),
    div[data-testid="stElementContainer"]:has(.section-gap),
    div[data-testid="stElementContainer"]:has(.section-gap-xs),
    div[data-testid="stElementContainer"]:has(.section-gap-small) {
        height: 14px !important;
        min-height: 14px !important;
        max-height: 14px !important;
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
        min-height: 106px !important;
        max-height: none !important;
        padding: 12px 13px !important;
    }            

                
    .kpi-value {
        font-size: 1.22rem !important;
        line-height: 1.12 !important;
        overflow-wrap: anywhere !important;
    }

    .kpi-help {
        font-size: 0.74rem !important;
        line-height: 1.25 !important;
    }            

    .method-grid {
        grid-template-columns: 1fr !important;
        gap: 12px !important;
    }

    .method-card {
        height: auto !important;
        min-height: auto !important;
        padding: 14px 15px !important;
    }

    .st-key-card_perfil,
    .st-key-card_aceptacion,
    .st-key-card_confianza,
    .st-key-card_regulacion {
        padding: 15px !important;
    }

    .hypothesis-box {
        padding: 14px !important;
        font-size: 0.82rem !important;
        line-height: 1.42 !important;
    }

    .progress-row {
        padding-right: 0 !important;
    }

    .progress-row-header {
        grid-template-columns: 1fr !important;
        gap: 4px !important;
    }

    .progress-row-header span:last-child {
        text-align: left !important;
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
        min-height: auto !important;
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
   Confianza electoral · estructura final H1 + H2 para defensa
   Pegar al final de dashboard/styles.py, dentro del <style>
   ========================================================= */

[class*="st-key-card_ce_"] {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 16px !important;
    padding: 18px 20px 20px 20px !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    overflow: hidden !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

[class*="st-key-card_ce_"] *,
[class*="st-key-card_ce_"] > div,
[class*="st-key-card_ce_"] [data-testid="stVerticalBlock"],
[class*="st-key-card_ce_"] [data-testid="stElementContainer"],
[class*="st-key-card_ce_"] [data-testid="stMarkdownContainer"],
[class*="st-key-card_ce_"] [data-testid="stPlotlyChart"] {
    max-width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
}

[class*="st-key-card_ce_"] > div,
[class*="st-key-card_ce_"] [data-testid="stVerticalBlock"],
[class*="st-key-card_ce_"] [data-testid="stElementContainer"],
[class*="st-key-card_ce_"] [data-testid="stMarkdownContainer"],
[class*="st-key-card_ce_"] [data-testid="stPlotlyChart"] {
    background-color: #ffffff !important;
}

[class*="st-key-card_ce_"] .js-plotly-plot,
[class*="st-key-card_ce_"] .plotly,
[class*="st-key-card_ce_"] .plot-container,
[class*="st-key-card_ce_"] .svg-container {
    background: #ffffff !important;
    width: 100% !important;
    max-width: 100% !important;
}

/* Elimina la altura rígida anterior de 430px */
.st-key-card_ce_limpieza,
.st-key-card_ce_fraude,
.st-key-card_ce_influencia_voto,
.st-key-card_ce_cambio_confianza {
    height: auto !important;
    min-height: 340px !important;
    max-height: none !important;
    padding: 18px 20px 20px 20px !important;
}

.st-key-card_ce_interpretacion,
.st-key-card_ce_matriz,
.st-key-card_ce_heatmap,
.st-key-card_ce_dispersion,
.st-key-card_ce_edad_boxplot,
.st-key-card_ce_spearman,
.st-key-card_ce_metodologia,
.st-key-card_ce_h2_definicion,
.st-key-card_ce_h2_resumen,
.st-key-card_ce_h2_lineas,
.st-key-card_ce_h2_heatmap,
.st-key-card_ce_h2_tabla {
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
}

.ce-section-gap {
    height: 12px !important;
    min-height: 12px !important;
    max-height: 12px !important;
    margin: 0 !important;
    padding: 0 !important;
    display: block !important;
}

div[data-testid="stElementContainer"]:has(.ce-section-gap) {
    height: 12px !important;
    min-height: 12px !important;
    max-height: 12px !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

.ce-age-grid {
    display: grid !important;
    grid-template-columns: repeat(5, minmax(0, 1fr)) !important;
    gap: 10px !important;
    margin-top: 12px !important;
}

.ce-age-card {
    background: #f8fafc !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
    padding: 12px 10px !important;
    text-align: center !important;
    min-height: 105px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}

.ce-age-title {
    color: #334155 !important;
    font-size: 0.78rem !important;
    font-weight: 850 !important;
    line-height: 1.25 !important;
    margin-bottom: 5px !important;
}

.ce-age-value {
    color: #059669 !important;
    font-size: 1.25rem !important;
    font-weight: 900 !important;
    line-height: 1.05 !important;
    margin-bottom: 5px !important;
}

.ce-age-text {
    color: #64748b !important;
    font-size: 0.72rem !important;
    line-height: 1.25 !important;
}

/* H2: hipótesis y moderación */
.ce-hypothesis-box {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    color: #1d4ed8 !important;
    border-radius: 14px !important;
    padding: 13px 15px !important;
    font-size: 0.87rem !important;
    line-height: 1.45 !important;
    margin-top: 8px !important;
}

.ce-h2-grid {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    gap: 12px !important;
    margin: 4px 0 12px 0 !important;
}

.ce-h2-card {
    border-radius: 15px !important;
    padding: 15px 16px !important;
    border: 1px solid #e5e7eb !important;
    min-height: 128px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    box-sizing: border-box !important;
}

.ce-h2-card.blue {
    background: #eff6ff !important;
    border-color: #bfdbfe !important;
}

.ce-h2-card.green {
    background: #ecfdf5 !important;
    border-color: #a7f3d0 !important;
}

.ce-h2-card.yellow {
    background: #fffbeb !important;
    border-color: #fde68a !important;
}

.ce-h2-card.red {
    background: #fff7ed !important;
    border-color: #fed7aa !important;
}

.ce-h2-label {
    color: #64748b !important;
    font-size: 0.72rem !important;
    font-weight: 850 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.035em !important;
    line-height: 1.25 !important;
    margin-bottom: 8px !important;
}

.ce-h2-value {
    color: #0f172a !important;
    font-size: clamp(1.25rem, 2vw, 1.55rem) !important;
    font-weight: 900 !important;
    line-height: 1.05 !important;
    margin-bottom: 7px !important;
}

.ce-h2-value.small {
    font-size: clamp(0.95rem, 1.35vw, 1.12rem) !important;
    line-height: 1.18 !important;
}

.ce-h2-text {
    color: #64748b !important;
    font-size: 0.78rem !important;
    line-height: 1.35 !important;
}

.ce-method-panel {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
    color: #334155 !important;
}

.ce-method-title {
    font-size: 1.02rem !important;
    font-weight: 900 !important;
    color: #0f172a !important;
    margin-bottom: 14px !important;
}

.ce-method-grid {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 12px !important;
}

.ce-method-item {
    background: #f8fafc !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 13px !important;
    padding: 13px 14px !important;
    color: #475569 !important;
    font-size: 0.82rem !important;
    line-height: 1.42 !important;
}

.ce-method-item strong {
    color: #0f172a !important;
}

/* =========================================================
   Confianza electoral · lectura metodológica con colores suaves
   ========================================================= */

.ce-method-grid .ce-method-item:nth-child(1) {
    background: #eff6ff !important;
    border-color: #bfdbfe !important;
}

.ce-method-grid .ce-method-item:nth-child(2) {
    background: #fffbeb !important;
    border-color: #fde68a !important;
}

.ce-method-grid .ce-method-item:nth-child(3) {
    background: #ecfdf5 !important;
    border-color: #a7f3d0 !important;
}

.ce-method-grid .ce-method-item:nth-child(4) {
    background: #f5f3ff !important;
    border-color: #ddd6fe !important;
}

.ce-method-grid .ce-method-item:nth-child(1) strong {
    color: #1d4ed8 !important;
}

.ce-method-grid .ce-method-item:nth-child(2) strong {
    color: #92400e !important;
}

.ce-method-grid .ce-method-item:nth-child(3) strong {
    color: #047857 !important;
}

.ce-method-grid .ce-method-item:nth-child(4) strong {
    color: #6d28d9 !important;
}

/* Tabla técnica H2 centrada */
.ce-h2-table-wrap {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    overflow-x: auto !important;
    padding: 4px 0 8px 0 !important;
}

.ce-h2-table {
    width: auto !important;
    min-width: 860px !important;
    max-width: 1120px !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    font-size: 0.86rem !important;
}

.ce-h2-table th {
    background: #f8fafc !important;
    color: #64748b !important;
    font-weight: 850 !important;
    text-align: center !important;
    padding: 11px 12px !important;
    border-bottom: 1px solid #e5e7eb !important;
    border-right: 1px solid #e5e7eb !important;
    white-space: nowrap !important;
}

.ce-h2-table td {
    color: #0f172a !important;
    text-align: center !important;
    padding: 12px 12px !important;
    border-bottom: 1px solid #eef2f7 !important;
    border-right: 1px solid #eef2f7 !important;
    white-space: nowrap !important;
}

.ce-h2-table tr:last-child td {
    border-bottom: none !important;
}

.ce-h2-table th:last-child,
.ce-h2-table td:last-child {
    border-right: none !important;
}

.ce-h2-table td.left {
    text-align: left !important;
    font-weight: 750 !important;
    min-width: 150px !important;
}

/* Síntesis interpretativa del resumen */
.ce-summary-reading {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    gap: 12px !important;
    margin-top: 6px !important;
}

.ce-summary-reading-item {
    border-radius: 14px !important;
    padding: 14px 15px !important;
    min-height: 118px !important;
    border: 1px solid #e5e7eb !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}

.ce-summary-reading-item strong {
    color: #0f172a !important;
    font-size: 0.86rem !important;
    font-weight: 900 !important;
    line-height: 1.25 !important;
    margin-bottom: 8px !important;
}

.ce-summary-reading-item span {
    color: #64748b !important;
    font-size: 0.82rem !important;
    line-height: 1.38 !important;
}

.ce-summary-reading-item.blue {
    background: #eff6ff !important;
    border-color: #bfdbfe !important;
}

.ce-summary-reading-item.red {
    background: #fff7ed !important;
    border-color: #fed7aa !important;
}

.ce-summary-reading-item.yellow {
    background: #fffbeb !important;
    border-color: #fde68a !important;
}

/* Matriz H2 */
.st-key-card_ce_h2_heatmap [data-testid="stPlotlyChart"] {
    display: flex !important;
    justify-content: center !important;
}

.st-key-card_ce_h2_heatmap .analysis-note-compact {
    margin-top: 4px !important;
}

@media (max-width: 1100px) {
    .ce-summary-reading {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
}

@media (max-width: 760px) {
    .ce-summary-reading {
        grid-template-columns: 1fr !important;
    }

    .ce-h2-table {
        min-width: 760px !important;
        font-size: 0.78rem !important;
    }

    .ce-h2-table th,
    .ce-h2-table td {
        padding: 9px 10px !important;
    }
}                

@media (max-width: 1100px) {
    .ce-age-grid,
    .ce-h2-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }

    .ce-method-grid {
        grid-template-columns: 1fr !important;
    }

    .st-key-card_ce_limpieza,
    .st-key-card_ce_fraude,
    .st-key-card_ce_influencia_voto,
    .st-key-card_ce_cambio_confianza {
        min-height: auto !important;
    }
}

@media (max-width: 760px) {
    [class*="st-key-card_ce_"] {
        padding: 15px !important;
        border-radius: 14px !important;
    }

    .ce-age-grid,
    .ce-h2-grid {
        grid-template-columns: 1fr !important;
    }

    .ce-age-card,
    .ce-h2-card {
        min-height: auto !important;
    }

    .ce-method-panel {
        padding: 15px !important;
    }
}
                
/* =========================================================
   Modelos predictivos · visual integrado tipo prototipo
   ========================================================= */

[class*="st-key-card_mp_"] {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 18px !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    box-sizing: border-box !important;
    overflow: visible !important;
}

[class*="st-key-card_mp_"],
[class*="st-key-card_mp_"] > div,
[class*="st-key-card_mp_"] [data-testid="stVerticalBlock"],
[class*="st-key-card_mp_"] [data-testid="stElementContainer"],
[class*="st-key-card_mp_"] [data-testid="stMarkdownContainer"],
[class*="st-key-card_mp_"] [data-testid="stPlotlyChart"] {
    background-color: #ffffff !important;
    max-width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
}

/* Tarjetas principales */
.st-key-card_mp_metricas,
.st-key-card_mp_configuracion {
    padding: 22px 24px 24px 24px !important;
    min-height: 495px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
}

.st-key-card_mp_configuracion .mp-insight {
    min-height: auto !important;
}

/* Tarjetas internas de tabs */
.st-key-card_mp_importancia,
.st-key-card_mp_clases,
.st-key-card_mp_estabilidad,
.st-key-card_mp_interpretacion,
.st-key-card_mp_simulador_base {
    padding: 22px 24px 26px 24px !important;
}

/* Encabezados */
[class*="st-key-card_mp_"] .section-title-card {
    font-size: 1.08rem !important;
    font-weight: 900 !important;
    color: #0f172a !important;
    line-height: 1.25 !important;
    margin-bottom: 5px !important;
}

[class*="st-key-card_mp_"] .section-subtitle-card {
    font-size: 0.84rem !important;
    color: #64748b !important;
    line-height: 1.38 !important;
    margin-bottom: 12px !important;
}

/* Plotly */
[class*="st-key-card_mp_"] [data-testid="stPlotlyChart"],
[class*="st-key-card_mp_"] .js-plotly-plot,
[class*="st-key-card_mp_"] .plotly,
[class*="st-key-card_mp_"] .plot-container,
[class*="st-key-card_mp_"] .svg-container {
    width: 100% !important;
    max-width: 100% !important;
    background: #ffffff !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 14px !important;
    border-bottom: 1px solid #e5e7eb !important;
}

.stTabs [data-baseweb="tab"] {
    padding: 10px 8px !important;
    color: #64748b !important;
    font-size: 0.84rem !important;
    font-weight: 750 !important;
}

.stTabs [aria-selected="true"] {
    color: #2563eb !important;
    font-weight: 900 !important;
}

/* =========================================================
   Importancia de variables
   ========================================================= */

.mp-mini-grid {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 12px !important;
    margin-top: 14px !important;
}

.mp-rank-card {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    background: #f8fafc !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
    padding: 13px 14px !important;
    min-height: 78px !important;
    box-sizing: border-box !important;
}

.mp-rank-badge {
    width: 30px !important;
    height: 30px !important;
    min-width: 30px !important;
    border-radius: 999px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0.78rem !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    background: #2563eb !important;
}

.mp-rank-title {
    font-size: 0.84rem !important;
    font-weight: 850 !important;
    color: #334155 !important;
    line-height: 1.2 !important;
}

.mp-rank-sub {
    font-size: 0.76rem !important;
    color: #64748b !important;
    margin-top: 3px !important;
    line-height: 1.25 !important;
}

.mp-insight {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    color: #1d4ed8 !important;
    border-radius: 14px !important;
    padding: 13px 15px !important;
    min-height: 78px !important;
    font-size: 0.82rem !important;
    line-height: 1.42 !important;
    display: block !important;
    box-sizing: border-box !important;
}

.mp-insight strong {
    color: #1d4ed8 !important;
    font-weight: 900 !important;
}

/* =========================================================
   Matriz de confusión
   ========================================================= */

.st-key-card_mp_clases {
    overflow-x: auto !important;
}

.mp-matrix-wrap {
    width: 100% !important;
    overflow-x: auto !important;
    padding: 12px 0 4px 0 !important;
}

.mp-matrix-title {
    text-align: center !important;
    color: #64748b !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
    margin-bottom: 10px !important;
}

table.mp-matrix {
    border-collapse: separate !important;
    border-spacing: 6px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

table.mp-matrix th {
    color: #334155 !important;
    background: #f8fafc !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-weight: 850 !important;
    text-align: center !important;
    padding: 8px 10px !important;
    white-space: nowrap !important;
}

table.mp-matrix td.real-label {
    color: #334155 !important;
    font-size: 0.78rem !important;
    font-weight: 850 !important;
    text-align: right !important;
    padding-right: 8px !important;
    white-space: nowrap !important;
}

table.mp-matrix td.cell {
    min-width: 82px !important;
    height: 58px !important;
    border-radius: 10px !important;
    text-align: center !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.28) !important;
}

.mp-cell-count {
    display: block !important;
    font-size: 0.92rem !important;
    line-height: 1.05 !important;
    font-weight: 900 !important;
}

.mp-cell-pct {
    display: block !important;
    font-size: 0.72rem !important;
    line-height: 1 !important;
    font-weight: 750 !important;
    opacity: 0.9 !important;
    margin-top: 4px !important;
}

.mp-legend-row {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 14px !important;
    align-items: center !important;
    justify-content: center !important;
    border-top: 1px solid #eef2f7 !important;
    padding-top: 12px !important;
    margin-top: 12px !important;
    color: #475569 !important;
    font-size: 0.82rem !important;
}

.mp-swatch {
    width: 12px !important;
    height: 12px !important;
    border-radius: 4px !important;
    display: inline-block !important;
    margin-right: 6px !important;
    vertical-align: -1px !important;
}

.mp-accuracy {
    background: #ecfdf5 !important;
    color: #047857 !important;
    border: 1px solid #a7f3d0 !important;
    border-radius: 999px !important;
    padding: 6px 10px !important;
    font-size: 0.78rem !important;
    font-weight: 900 !important;
}

/* =========================================================
   Estabilidad
   ========================================================= */

.mp-stability-grid {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    gap: 12px !important;
    margin-top: 14px !important;
}

.mp-soft-card {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 16px !important;
    padding: 15px 16px !important;
    min-height: 116px !important;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04) !important;
    box-sizing: border-box !important;
}

/* =========================================================
   Interpretación técnica
   ========================================================= */

.mp-rule-grid {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 14px !important;
    margin-top: 14px !important;
}

.mp-rule-card {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 16px !important;
    padding: 16px 17px !important;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04) !important;
    box-sizing: border-box !important;
}

.mp-rule-head {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    margin-bottom: 12px !important;
}

.mp-rule-num {
    width: 28px !important;
    height: 28px !important;
    min-width: 28px !important;
    border-radius: 999px !important;
    background: #f1f5f9 !important;
    color: #334155 !important;
    display: inline-flex !important;
    justify-content: center !important;
    align-items: center !important;
    font-size: 0.72rem !important;
    font-weight: 900 !important;
}

.mp-rule-chip {
    border-radius: 999px !important;
    padding: 5px 9px !important;
    font-size: 0.76rem !important;
    font-weight: 850 !important;
    border: 1px solid #e2e8f0 !important;
}

.mp-rule-code {
    background: #f8fafc !important;
    border: 1px solid #eef2f7 !important;
    border-radius: 12px !important;
    padding: 10px 11px !important;
    color: #334155 !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    font-size: 0.78rem !important;
    line-height: 1.35 !important;
    min-height: 48px !important;
}

.mp-rule-desc {
    color: #475569 !important;
    font-size: 0.82rem !important;
    line-height: 1.42 !important;
    margin: 12px 0 10px 0 !important;
}

.mp-rule-meta {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    border-top: 1px solid #eef2f7 !important;
    padding-top: 10px !important;
    color: #64748b !important;
    font-size: 0.76rem !important;
}

.mp-progress {
    height: 7px !important;
    background: #e2e8f0 !important;
    border-radius: 999px !important;
    overflow: hidden !important;
    flex: 1 !important;
}

.mp-progress > span {
    display: block !important;
    height: 100% !important;
    background: #60a5fa !important;
    border-radius: 999px !important;
}

/* =========================================================
   Simulador
   ========================================================= */

.st-key-card_mp_simulador_base .mp-sim-context {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    color: #1d4ed8 !important;
    border-radius: 14px !important;
    padding: 12px 14px !important;
    font-size: 0.83rem !important;
    line-height: 1.42 !important;
    margin-bottom: 14px !important;
}

.mp-result-card {
    border-radius: 16px !important;
    padding: 16px 17px !important;
    border: 1px solid #e5e7eb !important;
    background: #ffffff !important;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04) !important;
    box-sizing: border-box !important;
}

.mp-result-title {
    font-size: 0.78rem !important;
    color: #64748b !important;
    font-weight: 850 !important;
    margin-bottom: 6px !important;
}

.mp-result-value {
    font-size: 1.08rem !important;
    font-weight: 900 !important;
    margin-bottom: 10px !important;
}

.mp-sim-chip-row {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 7px !important;
    margin-top: 14px !important;
    padding-top: 12px !important;
    border-top: 1px solid #eef2f7 !important;
}

.mp-sim-chip {
    display: inline-flex !important;
    align-items: center !important;
    border-radius: 999px !important;
    background: #f8fafc !important;
    color: #475569 !important;
    border: 1px solid #e2e8f0 !important;
    padding: 6px 9px !important;
    font-size: 0.72rem !important;
    font-weight: 800 !important;
}

.mp-dist-row {
    margin-top: 9px !important;
}

.mp-dist-head {
    display: flex !important;
    justify-content: space-between !important;
    gap: 10px !important;
    font-size: 0.76rem !important;
    color: #64748b !important;
    margin-bottom: 4px !important;
}

.mp-dist-track {
    width: 100% !important;
    height: 7px !important;
    background: #e2e8f0 !important;
    border-radius: 999px !important;
    overflow: hidden !important;
}

.mp-dist-fill {
    height: 100% !important;
    border-radius: 999px !important;
    display: block !important;
}

.mp-method-mini {
    color: #64748b !important;
    font-size: 0.76rem !important;
    line-height: 1.35 !important;
    margin-top: 10px !important;
    border-top: 1px solid #eef2f7 !important;
    padding-top: 10px !important;
}

/* Notas dentro del módulo */
[class*="st-key-card_mp_"] .analysis-note-compact {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    color: #1d4ed8 !important;
}

[class*="st-key-card_mp_"] .analysis-note-compact-green {
    background: #ecfdf5 !important;
    border: 1px solid #a7f3d0 !important;
    color: #047857 !important;
}

[class*="st-key-card_mp_"] .analysis-note-compact-yellow,
[class*="st-key-card_mp_"] .alert-warning {
    background: #fffbeb !important;
    border: 1px solid #fde68a !important;
    color: #b45309 !important;
}

[class*="st-key-card_mp_"] .analysis-note-compact-red,
[class*="st-key-card_mp_"] .alert-danger {
    background: #fff7ed !important;
    border: 1px solid #fed7aa !important;
    color: #c2410c !important;
}

/* Responsive */
@media (max-width: 1100px) {
    .st-key-card_mp_metricas,
    .st-key-card_mp_configuracion {
        min-height: auto !important;
    }

    .mp-stability-grid,
    .mp-mini-grid,
    .mp-rule-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
}

@media (max-width: 760px) {
    [class*="st-key-card_mp_"] {
        padding: 16px !important;
        border-radius: 15px !important;
    }

    .mp-stability-grid,
    .mp-mini-grid,
    .mp-rule-grid {
        grid-template-columns: 1fr !important;
    }

    .st-key-card_mp_clases .mp-legend-row {
        justify-content: flex-start !important;
    }

    table.mp-matrix td.cell {
        min-width: 68px !important;
    }
}

/* =========================================================
   Evidencia digital y encuestas · bloque definitivo
   ========================================================= */

[class*="st-key-card_ed_"] {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 18px !important;
    padding: 22px 24px 26px 24px !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    overflow: visible !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

[class*="st-key-card_ed_"] *,
[class*="st-key-card_ed_"] > div,
[class*="st-key-card_ed_"] [data-testid="stVerticalBlock"],
[class*="st-key-card_ed_"] [data-testid="stElementContainer"],
[class*="st-key-card_ed_"] [data-testid="stMarkdownContainer"],
[class*="st-key-card_ed_"] [data-testid="stPlotlyChart"] {
    max-width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
}

[class*="st-key-card_ed_"] > div,
[class*="st-key-card_ed_"] [data-testid="stVerticalBlock"],
[class*="st-key-card_ed_"] [data-testid="stElementContainer"],
[class*="st-key-card_ed_"] [data-testid="stMarkdownContainer"],
[class*="st-key-card_ed_"] [data-testid="stPlotlyChart"] {
    background-color: #ffffff !important;
}

[class*="st-key-card_ed_"] .section-title-card {
    color: #0f172a !important;
    font-size: 1.04rem !important;
    font-weight: 900 !important;
    line-height: 1.25 !important;
    letter-spacing: -0.015em !important;
    margin-bottom: 5px !important;
}

[class*="st-key-card_ed_"] .section-subtitle-card {
    color: #64748b !important;
    font-size: 0.84rem !important;
    line-height: 1.45 !important;
    margin-bottom: 14px !important;
}

.ed-section-gap {
    height: 12px !important;
    min-height: 12px !important;
    max-height: 12px !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* KPI superiores */

.ed-kpi-grid {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    gap: 14px !important;
    margin: 4px 0 16px 0 !important;
}

.ed-kpi {
    border: 1px solid #e5e7eb !important;
    border-radius: 16px !important;
    padding: 13px 15px !important;
    min-height: 112px !important;
    height: auto !important;
    max-height: none !important;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.04) !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    position: relative !important;
}

/* Quitar línea superior anterior */
.ed-kpi::before {
    content: none !important;
    display: none !important;
}

.ed-kpi.blue {
    background: #eff6ff !important;
    border-color: #bfdbfe !important;
}

.ed-kpi.red {
    background: #fef2f2 !important;
    border-color: #fecaca !important;
}

.ed-kpi.green {
    background: #ecfdf5 !important;
    border-color: #a7f3d0 !important;
}

.ed-kpi.yellow {
    background: #fffbeb !important;
    border-color: #fde68a !important;
}

.ed-kpi.purple {
    background: #f5f3ff !important;
    border-color: #ddd6fe !important;
}

.ed-kpi.cyan {
    background: #ecfeff !important;
    border-color: #a5f3fc !important;
}

.ed-kpi-label {
    color: #64748b !important;
    font-size: 0.68rem !important;
    font-weight: 850 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    line-height: 1.25 !important;
    margin-bottom: 5px !important;
}

.ed-kpi-value {
    color: #0f172a !important;
    font-size: 1.42rem !important;
    font-weight: 850 !important;
    line-height: 1.08 !important;
    letter-spacing: 0 !important;
}

.ed-kpi-help {
    color: #64748b !important;
    font-size: 0.78rem !important;
    margin-top: 6px !important;
    line-height: 1.25 !important;
}



/* Cards internas de diseño metodológico y triangulación */
.ed-source-grid {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)) !important;
    gap: 14px !important;
    margin-top: 12px !important;
}

.ed-source-card {
    border-radius: 15px !important;
    padding: 16px 17px !important;
    border: 1px solid #e5e7eb !important;
    min-height: 132px !important;
    box-sizing: border-box !important;
    box-shadow: 0 1px 5px rgba(15, 23, 42, 0.035) !important;
}

.ed-source-card.blue {
    background: #f8fbff !important;
    border-color: #bfdbfe !important;
}

.ed-source-card.green {
    background: #f6fffb !important;
    border-color: #a7f3d0 !important;
}

.ed-source-card.yellow {
    background: #fffaf0 !important;
    border-color: #fde68a !important;
}

.ed-source-title {
    color: #0f172a !important;
    font-size: 0.88rem !important;
    font-weight: 900 !important;
    line-height: 1.25 !important;
    margin-bottom: 8px !important;
}

.ed-source-text {
    color: #64748b !important;
    font-size: 0.81rem !important;
    line-height: 1.48 !important;
}

/* Barras */
.ed-bar-row {
    width: 100% !important;
    max-width: 100% !important;
    padding-right: 18px !important;
    margin-bottom: 13px !important;
    box-sizing: border-box !important;
}

.ed-bar-row:last-child {
    margin-bottom: 4px !important;
}

.ed-bar-head {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) auto !important;
    gap: 12px !important;
    align-items: center !important;
    color: #334155 !important;
    font-size: 0.82rem !important;
    font-weight: 750 !important;
    line-height: 1.25 !important;
    margin-bottom: 6px !important;
}

.ed-bar-head span:first-child {
    min-width: 0 !important;
    overflow-wrap: anywhere !important;
}

.ed-bar-head span:last-child {
    white-space: nowrap !important;
    color: #0f172a !important;
    font-weight: 850 !important;
    text-align: right !important;
}

.ed-track {
    width: 100% !important;
    height: 15px !important;
    background: #eef2f7 !important;
    border-radius: 999px !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

.ed-fill {
    height: 100% !important;
    border-radius: 999px !important;
    background: #3b82f6 !important;
}

.ed-fill.blue { background: #2563eb !important; }
.ed-fill.red { background: #fb7185 !important; }
.ed-fill.green { background: #10b981 !important; }
.ed-fill.yellow { background: #f59e0b !important; }

/* Notas */
.ed-note-blue,
.ed-note-red,
.ed-note-green,
.ed-note-yellow {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    border-radius: 13px !important;
    padding: 12px 14px !important;
    font-size: 0.81rem !important;
    line-height: 1.42 !important;
    margin-top: 13px !important;
    overflow-wrap: break-word !important;
}

.ed-note-blue {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    border: 1px solid #bfdbfe !important;
}

.ed-note-red {
    background: #fff7ed !important;
    color: #c2410c !important;
    border: 1px solid #fed7aa !important;
}

.ed-note-green {
    background: #ecfdf5 !important;
    color: #047857 !important;
    border: 1px solid #a7f3d0 !important;
}

.ed-note-yellow {
    background: #fffbeb !important;
    color: #92400e !important;
    border: 1px solid #fde68a !important;
}

/* Resumen de sentimiento */
.ed-tone-grid {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
    gap: 12px !important;
    margin: 4px 0 16px 0 !important;
}

.ed-tone-card {
    border-radius: 15px !important;
    padding: 14px 15px !important;
    border: 1px solid #e5e7eb !important;
    min-height: 112px !important;
    box-sizing: border-box !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}

.ed-tone-card.blue {
    background: #f8fbff !important;
    border-color: #bfdbfe !important;
}

.ed-tone-card.green {
    background: #f6fffb !important;
    border-color: #a7f3d0 !important;
}

.ed-tone-card.yellow {
    background: #fffaf0 !important;
    border-color: #fde68a !important;
}

.ed-tone-title {
    color: #0f172a !important;
    font-size: 0.78rem !important;
    font-weight: 900 !important;
    line-height: 1.25 !important;
    margin-bottom: 7px !important;
}

.ed-tone-value {
    color: #0f172a !important;
    font-size: clamp(1.25rem, 2vw, 1.48rem) !important;
    font-weight: 900 !important;
    line-height: 1.05 !important;
    letter-spacing: -0.04em !important;
    margin-bottom: 7px !important;
}

.ed-tone-text {
    color: #64748b !important;
    font-size: 0.76rem !important;
    line-height: 1.35 !important;
}


.ed-tri-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-top: 12px;
    margin-bottom: 14px;
}

.ed-tri-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.045);
    min-height: 126px;
}

.ed-tri-card-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 10px;
}

.ed-tri-dimension {
    font-size: 0.98rem;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.25;
}

.ed-tri-badge {
    flex: 0 0 auto;
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 0.72rem;
    font-weight: 850;
    border: 1px solid transparent;
}

.ed-tri-badge.strong {
    background: #ecfdf5;
    color: #047857;
    border-color: #a7f3d0;
}

.ed-tri-badge.medium {
    background: #fffbeb;
    color: #92400e;
    border-color: #fde68a;
}

.ed-tri-badge.contextual {
    background: #eff6ff;
    color: #1d4ed8;
    border-color: #bfdbfe;
}

.ed-tri-badge.exploratory {
    background: #f5f3ff;
    color: #6d28d9;
    border-color: #ddd6fe;
}

.ed-tri-reading {
    font-size: 0.86rem;
    line-height: 1.45;
    color: #475569;
}

@media (max-width: 900px) {
    .ed-tri-grid {
        grid-template-columns: 1fr;
    }
}                

                
/* Plotly dentro del módulo */
[class*="st-key-card_ed_"] .js-plotly-plot,
[class*="st-key-card_ed_"] .plotly,
[class*="st-key-card_ed_"] .plot-container,
[class*="st-key-card_ed_"] .svg-container {
    background: #ffffff !important;
    width: 100% !important;
    max-width: 100% !important;
}

/* Responsive */
@media (max-width: 1250px) {
    .ed-kpi-grid,
    .interpretation-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }

    [class*="st-key-card_ed_"] {
        padding: 20px 22px 24px 22px !important;
    }
}

@media (max-width: 760px) {
    [class*="st-key-card_ed_"] {
        padding: 16px !important;
        border-radius: 15px !important;
    }

    .ed-kpi-grid,
    .interpretation-grid {
        grid-template-columns: 1fr !important;
    }

    .ed-kpi,
    .ed-source-card,
    .ed-tone-card {
        min-height: auto !important;
    }

    .ed-bar-head {
        grid-template-columns: 1fr !important;
        gap: 4px !important;
    }

    .ed-bar-head span:last-child {
        text-align: left !important;
    }
}

@media (min-width: 900px) {
    .st-key-card_ed_encuesta_exposicion,
    .st-key-card_ed_encuesta_falso,
    .st-key-card_ed_encuesta_automatizacion,
    .st-key-card_ed_encuesta_verificacion {
        min-height: unset !important;
        height: auto !important;
        overflow: visible !important;
    }

    .st-key-card_ed_encuesta_exposicion [data-testid="stVerticalBlock"],
    .st-key-card_ed_encuesta_falso [data-testid="stVerticalBlock"],
    .st-key-card_ed_encuesta_automatizacion [data-testid="stVerticalBlock"],
    .st-key-card_ed_encuesta_verificacion [data-testid="stVerticalBlock"] {
        height: auto !important;
        min-height: unset !important;
        display: block !important;
    }

    .st-key-card_ed_encuesta_exposicion div[data-testid="stElementContainer"]:has(.ed-note-blue),
    .st-key-card_ed_encuesta_falso div[data-testid="stElementContainer"]:has(.ed-note-red),
    .st-key-card_ed_encuesta_automatizacion div[data-testid="stElementContainer"]:has(.ed-note-yellow),
    .st-key-card_ed_encuesta_verificacion div[data-testid="stElementContainer"]:has(.ed-note-green) {
        margin-top: 12px !important;
    }
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
                
/* Reduce espacio horizontal global entre columnas */
[data-testid="stHorizontalBlock"] {
    gap: 0.65rem !important;
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
                
[class*="st-key-card_ed_"],
[class*="st-key-card_ed_"] > div,
[class*="st-key-card_ed_"] [data-testid="stVerticalBlock"],
[class*="st-key-card_ed_"] [data-testid="stElementContainer"],
[class*="st-key-card_ed_"] [data-testid="stMarkdownContainer"],
[class*="st-key-card_ed_"] [data-testid="stPlotlyChart"] {
    overflow: visible !important;
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
.mp-bar-row {
    width: 100% !important;
    max-width: 100% !important;
    padding-right: 22px !important;
    box-sizing: border-box !important;
}

.ed-bar-row {
    width: 100% !important;
    max-width: 100% !important;
    padding-right: 18px !important;
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

                

/* Tarjetas de percepción ciudadana: compactas y sin espacio sobrante */
.st-key-card_pc_aceptacion,
.st-key-card_pc_manipulacion,
.st-key-card_pc_desconfianza,
.st-key-card_pc_regulacion {
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    padding: 16px 18px 18px 18px !important;
}


/* Tarjetas de confianza electoral compactas */
.st-key-card_ce_limpieza,
.st-key-card_ce_fraude,
.st-key-card_ce_influencia_voto,
.st-key-card_ce_cambio_confianza {
    height: auto !important;
    min-height: 340px !important;
    max-height: none !important;
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

/* =========================================================
   Evidencia digital · ajuste final de resumen de sentimiento
   ========================================================= */

.st-key-card_ed_gdelt_tono {
    overflow: hidden !important;
}

/* Reserva espacio interno para que valores y barras no lleguen al borde */
.st-key-card_ed_gdelt_tono .ed-bar-row {
    padding-right: 42px !important;
    margin-bottom: 10px !important;
}

.st-key-card_ed_gdelt_tono .ed-bar-row:last-child {
    margin-bottom: 6px !important;
}

/* Mini tarjetas superiores más compactas */
.st-key-card_ed_gdelt_tono .ed-tone-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
    gap: 10px !important;
    margin: 2px 0 14px 0 !important;
}

.st-key-card_ed_gdelt_tono .ed-tone-card {
    min-height: 104px !important;
    padding: 12px 14px !important;
    overflow: hidden !important;
}

.st-key-card_ed_gdelt_tono .ed-tone-title {
    font-size: 0.74rem !important;
    line-height: 1.22 !important;
}

.st-key-card_ed_gdelt_tono .ed-tone-value {
    font-size: clamp(1.14rem, 1.55vw, 1.34rem) !important;
    line-height: 1.05 !important;
}

.st-key-card_ed_gdelt_tono .ed-tone-text {
    font-size: 0.72rem !important;
    line-height: 1.32 !important;
}

/* Nota inferior más pegada al contenido y sin espacio sobrante */
.st-key-card_ed_gdelt_tono .ed-note-yellow {
    margin-top: 10px !important;
    margin-bottom: 0 !important;
    padding: 12px 14px !important;
    font-size: 0.8rem !important;
    line-height: 1.38 !important;
}

/* Ajuste en pantallas medianas */
@media (max-width: 1180px) {
    .st-key-card_ed_gdelt_tono .ed-tone-grid {
        grid-template-columns: 1fr !important;
    }

    .st-key-card_ed_gdelt_tono .ed-tone-card {
        min-height: auto !important;
    }
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

    .method-grid {
        grid-template-columns: 1fr !important;
        gap: 12px !important;
    }

    .method-card {
        height: auto !important;
        min-height: auto !important;
    }            
                            
}

/* =========================================================
   Triangulación y Datos / Artefactos
   ========================================================= */

[class*="st-key-card_tri_"],
[class*="st-key-card_art_"] {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 16px !important;
    padding: 18px 20px 20px 20px !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.055) !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

[class*="st-key-card_tri_"] *,
[class*="st-key-card_art_"] * {
    background-color: transparent !important;
}

[class*="st-key-card_tri_"],
[class*="st-key-card_tri_"] > div,
[class*="st-key-card_tri_"] [data-testid="stVerticalBlock"],
[class*="st-key-card_tri_"] [data-testid="stElementContainer"],
[class*="st-key-card_tri_"] [data-testid="stMarkdownContainer"],
[class*="st-key-card_tri_"] [data-testid="stPlotlyChart"],
[class*="st-key-card_art_"],
[class*="st-key-card_art_"] > div,
[class*="st-key-card_art_"] [data-testid="stVerticalBlock"],
[class*="st-key-card_art_"] [data-testid="stElementContainer"],
[class*="st-key-card_art_"] [data-testid="stMarkdownContainer"],
[class*="st-key-card_art_"] [data-testid="stPlotlyChart"] {
    background-color: #ffffff !important;
}

/* Mantener notas con color dentro de tarjetas */
[class*="st-key-card_tri_"] .analysis-note-compact,
[class*="st-key-card_art_"] .analysis-note-compact {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    color: #1d4ed8 !important;
}

[class*="st-key-card_tri_"] .analysis-note-compact-green,
[class*="st-key-card_art_"] .analysis-note-compact-green {
    background: #ecfdf5 !important;
    border: 1px solid #a7f3d0 !important;
    color: #047857 !important;
}

[class*="st-key-card_tri_"] .analysis-note-compact-yellow,
[class*="st-key-card_art_"] .analysis-note-compact-yellow {
    background: #fffbeb !important;
    border: 1px solid #fde68a !important;
    color: #b45309 !important;
}

[class*="st-key-card_tri_"] .analysis-note-compact-red,
[class*="st-key-card_art_"] .analysis-note-compact-red {
    background: #fff7ed !important;
    border: 1px solid #fed7aa !important;
    color: #c2410c !important;
}

/* Header común de tarjetas */
.card-header-soft {
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%) !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 10px 12px !important;
    margin-bottom: 10px !important;
}

.card-header-soft .section-title-card {
    font-size: 1.12rem !important;
    line-height: 1.25 !important;
    margin-bottom: 5px !important;
}

.card-header-soft .section-subtitle-card {
    font-size: 0.84rem !important;
    line-height: 1.35 !important;
    margin-bottom: 0 !important;
}

/* Tablas más legibles en estas secciones */
[class*="st-key-card_tri_"] [data-testid="stDataFrame"],
[class*="st-key-card_art_"] [data-testid="stDataFrame"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Selectores y buscadores dentro de tarjetas */
[class*="st-key-card_tri_"] [data-baseweb="select"],
[class*="st-key-card_art_"] [data-baseweb="select"],
[class*="st-key-card_tri_"] input,
[class*="st-key-card_art_"] input {
    font-size: 0.88rem !important;
}

/* Tarjetas internas de fuentes en triangulación */
.st-key-card_tri_fuente_encuesta,
.st-key-card_tri_fuente_digital,
.st-key-card_tri_fuente_modelo {
    background: #f8fafc !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
    padding: 14px !important;
    box-shadow: none !important;
}

/* Cards de descargas más compactas */
.st-key-card_art_download_0,
.st-key-card_art_download_1,
.st-key-card_art_download_2,
.st-key-card_art_download_3 {
    min-height: 230px !important;
}

/* Ajuste de botones de descarga */
[class*="st-key-card_tri_"] div[data-testid="stDownloadButton"] button,
[class*="st-key-card_art_"] div[data-testid="stDownloadButton"] button {
    border-radius: 12px !important;
    font-weight: 750 !important;
    border: 1px solid #bfdbfe !important;
    background: #eff6ff !important;
    color: #1d4ed8 !important;
}

/* Responsive */
@media (max-width: 900px) {
    [class*="st-key-card_tri_"],
    [class*="st-key-card_art_"] {
        padding: 15px !important;
        border-radius: 14px !important;
    }

    .st-key-card_art_download_0,
    .st-key-card_art_download_1,
    .st-key-card_art_download_2,
    .st-key-card_art_download_3 {
        min-height: auto !important;
    }
}

[class*="st-key-card_"] button [data-testid="stMarkdownContainer"],
[class*="st-key-card_"] button [data-testid="stMarkdownContainer"] * {
    background: transparent !important;
    color: inherit !important;
}

[class*="st-key-card_"] div[data-testid="stFormSubmitButton"] button[kind="primary"] {
    background: #2563eb !important;
    border: 1px solid #2563eb !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    font-weight: 850 !important;
    min-height: 42px !important;
}

[class*="st-key-card_"] div[data-testid="stFormSubmitButton"] button[kind="primary"] p,
[class*="st-key-card_"] div[data-testid="stFormSubmitButton"] button[kind="primary"] span {
    color: #ffffff !important;
}                 
             
</style>
""", unsafe_allow_html=True)
    
