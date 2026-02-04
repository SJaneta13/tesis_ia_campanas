"""
Interfaz intuitiva para el análisis de campañas con IA
Streamlit app para visualizar y explorar los análisis de sentimiento, tópicos y modelos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import json

# Configuración de página
st.set_page_config(
    page_title="Análisis IA Campañas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Barra lateral con navegación
st.sidebar.image("https://via.placeholder.com/150", use_container_width=True)
st.sidebar.title("🗂️ Navegación")

pages = {
    "📈 Dashboard": "dashboard",
    "💬 Análisis de Sentimiento": "sentiment",
    "📚 Modelado de Tópicos": "topics",
    "🤖 Modelos ML": "models",
    "📊 Comparación de Casos": "comparison",
    "⚙️ Configuración": "config"
}

selected_page = st.sidebar.radio("Selecciona una sección:", list(pages.keys()))
page = pages[selected_page]

# Variables de sesión
if 'current_case' not in st.session_state:
    st.session_state.current_case = "case1_es"

# ============================================================================
# PÁGINA: DASHBOARD
# ============================================================================
if page == "dashboard":
    st.title("📊 Dashboard de Análisis de Campañas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📰 Noticias Analizadas",
            value="2,547",
            delta="↑ 23% esta semana",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="😊 Sentimiento Positivo",
            value="62%",
            delta="↑ 5%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="🤖 IA Relacionada",
            value="1,428",
            delta="↑ 12%",
            delta_color="normal"
        )
    
    st.divider()
    
    # Gráficos de ejemplo
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sentimiento a lo Largo del Tiempo")
        dates = pd.date_range('2025-01-01', periods=30)
        data = pd.DataFrame({
            'Fecha': dates,
            'Positivo': [60 + i*0.5 for i in range(30)],
            'Neutral': [25 - i*0.2 for i in range(30)],
            'Negativo': [15 - i*0.3 for i in range(30)]
        })
        fig = px.area(data, x='Fecha', y=['Positivo', 'Neutral', 'Negativo'],
                     title='Evolución del Sentimiento',
                     color_discrete_map={
                         'Positivo': '#2ecc71',
                         'Neutral': '#f39c12',
                         'Negativo': '#e74c3c'
                     })
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Distribución de Casos")
        cases_data = pd.DataFrame({
            'Caso': ['España', 'Internacional', 'Ecuador'],
            'Artículos': [1200, 850, 497]
        })
        fig = px.pie(cases_data, values='Artículos', names='Caso',
                    title='Distribución por Caso',
                    color_discrete_sequence=['#3498db', '#e74c3c', '#f39c12'])
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PÁGINA: ANÁLISIS DE SENTIMIENTO
# ============================================================================
elif page == "sentiment":
    st.title("💬 Análisis de Sentimiento")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_case = st.selectbox(
            "Selecciona un caso:",
            options=["España (case1_es)", "Internacional (case2_en)", "Ecuador Media (case3_ec)"],
            key="case_sentiment"
        )
    with col2:
        st.write("")  # Espaciador
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        ai_filter = st.selectbox("Filtrar por IA:", 
                                 ["Todos", "Relacionado con IA", "No relacionado"])
    with col2:
        sentiment_filter = st.multiselect("Filtrar por sentimiento:",
                                         ["Positivo", "Neutral", "Negativo"],
                                         default=["Positivo", "Neutral", "Negativo"])
    with col3:
        st.write("")  # Espaciador
    
    st.divider()
    
    # Visualizaciones
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución de Sentimientos")
        sentiment_data = pd.DataFrame({
            'Sentimiento': ['Positivo', 'Neutral', 'Negativo'],
            'Cantidad': [1450, 720, 377],
            'Porcentaje': [62, 31, 7]
        })
        fig = px.bar(sentiment_data, x='Sentimiento', y='Cantidad',
                    color='Sentimiento',
                    color_discrete_map={
                        'Positivo': '#2ecc71',
                        'Neutral': '#f39c12',
                        'Negativo': '#e74c3c'
                    },
                    title='Conteo de Sentimientos')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Sentimiento por Tipo de Contenido")
        content_data = pd.DataFrame({
            'Tipo': ['IA Relacionada', 'No IA'],
            'Positivo': [920, 530],
            'Neutral': [380, 340],
            'Negativo': [128, 249]
        })
        fig = px.bar(content_data, x='Tipo', y=['Positivo', 'Neutral', 'Negativo'],
                    barmode='group',
                    title='Sentimiento por Tipo de Contenido',
                    color_discrete_map={
                        'Positivo': '#2ecc71',
                        'Neutral': '#f39c12',
                        'Negativo': '#e74c3c'
                    })
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("📋 Artículos Recientes")
    
    articles = pd.DataFrame({
        'Título': [
            'Nueva IA revoluciona sector energético',
            'Debates éticos sobre IA en política',
            'Empresas invierten más en inteligencia artificial'
        ],
        'Fecha': pd.date_range('2025-01-30', periods=3),
        'Sentimiento': ['Positivo', 'Neutral', 'Positivo'],
        'Relevancia IA': ['Alta', 'Alta', 'Alta'],
        'Fuente': ['Tech News', 'BBC News', 'Reuters']
    })
    
    st.dataframe(articles, use_container_width=True, hide_index=True)

# ============================================================================
# PÁGINA: MODELADO DE TÓPICOS
# ============================================================================
elif page == "topics":
    st.title("📚 Modelado de Tópicos")
    
    st.info("💡 Los tópicos se identifican automáticamente usando LDA (Latent Dirichlet Allocation)")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        case_selected = st.selectbox("Caso:", 
                                     ["España", "Internacional", "Ecuador"],
                                     key="case_topics")
    with col2:
        num_topics = st.slider("Número de tópicos:", 3, 20, 8)
    
    st.divider()
    
    # Distribución de tópicos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tópicos Principales")
        topics_data = pd.DataFrame({
            'Tópico': [f'Tópico {i+1}' for i in range(8)],
            'Palabras Clave': [
                'gobierno, política, reforma',
                'tecnología, innovación, startup',
                'medio ambiente, sostenibilidad',
                'economía, inversión, mercado',
                'educación, estudiantes, escuela',
                'salud, médico, hospital',
                'derechos, justicia, legal',
                'deportes, atleta, competencia'
            ],
            'Frecuencia': [245, 189, 156, 143, 127, 98, 87, 72]
        })
        fig = px.bar(topics_data, x='Frecuencia', y='Tópico',
                    orientation='h',
                    title='Distribución de Tópicos',
                    color='Frecuencia',
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Cobertura de Tópicos")
        for idx, row in topics_data.iterrows():
            with st.expander(f"**{row['Tópico']}** ({row['Frecuencia']} artículos)"):
                st.write(f"**Palabras clave:** {row['Palabras Clave']}")
                st.progress(row['Frecuencia']/245)

# ============================================================================
# PÁGINA: MODELOS ML
# ============================================================================
elif page == "models":
    st.title("🤖 Modelos de Machine Learning")
    
    st.markdown("### Modelos Entrenados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Random Forest",
            value="92.3%",
            delta="Precisión",
            delta_color="normal"
        )
        st.text("Datos: 2,547 artículos")
        st.text("Parámetros: 100 árboles")
        st.progress(0.923)
    
    with col2:
        st.metric(
            label="SVM (RBF)",
            value="89.7%",
            delta="Precisión",
            delta_color="normal"
        )
        st.text("Datos: 2,547 artículos")
        st.text("Kernel: RBF")
        st.progress(0.897)
    
    st.divider()
    
    st.subheader("Matriz de Confusión - Random Forest")
    
    confusion_matrix = pd.DataFrame({
        'Predicción IA': [1428, 45, 74],
        'Predicción No-IA': [78, 987, 2]
    }, index=['Real IA', 'Real No-IA', 'Otros'])
    
    fig = px.imshow(confusion_matrix,
                   labels=dict(x="Predicción", y="Real", color="Cantidad"),
                   title="Matriz de Confusión",
                   color_continuous_scale='Blues',
                   text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PÁGINA: COMPARACIÓN DE CASOS
# ============================================================================
elif page == "comparison":
    st.title("📊 Comparación Entre Casos")
    
    comparison_data = pd.DataFrame({
        'Métrica': [
            'Total de Artículos',
            'Positivo %',
            'Neutral %',
            'Negativo %',
            'IA Relacionada %',
            'Tópicos Principales'
        ],
        'España': [1200, 64, 28, 8, 58, 8],
        'Internacional': [850, 60, 33, 7, 62, 8],
        'Ecuador': [497, 59, 31, 10, 55, 6]
    })
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(comparison_data, x='Métrica', 
                    y=['España', 'Internacional', 'Ecuador'],
                    barmode='group',
                    title='Comparación de Casos',
                    color_discrete_sequence=['#3498db', '#e74c3c', '#f39c12'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col1:
        st.subheader("Tabla Comparativa")
        st.dataframe(comparison_data, use_container_width=True, hide_index=True)

# ============================================================================
# PÁGINA: CONFIGURACIÓN
# ============================================================================
elif page == "config":
    st.title("⚙️ Configuración")
    
    st.subheader("Ajustes Generales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📂 Directorios")
        backend_path = st.text_input("Ruta backend/public:", 
                                     value="backend/public")
        data_path = st.text_input("Ruta datos:", 
                                  value="data/processed")
    
    with col2:
        st.markdown("#### 🎨 Tema")
        theme = st.selectbox("Tema de color:", 
                            ["Claro", "Oscuro", "Auto"])
        language = st.selectbox("Idioma:", 
                               ["Español", "English"])
    
    st.divider()
    
    st.subheader("🔄 Sincronización de Datos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.success("✓ Datos actualizados correctamente")
    
    with col2:
        if st.button("📁 Limpiar Caché", use_container_width=True):
            st.info("Caché limpiado")
    
    with col3:
        if st.button("💾 Exportar Resultados", use_container_width=True):
            st.success("✓ Archivos listos para descargar")
    
    st.divider()
    
    st.subheader("ℹ️ Información del Sistema")
    
    system_info = {
        'Versión': '1.0.0',
        'Python': '3.11.9',
        'Última actualización': '2025-02-03',
        'Modelos entrenados': 2,
        'Casos analizados': 3
    }
    
    for key, value in system_info.items():
        st.metric(label=key, value=value)

# ============================================================================
# PIE DE PÁGINA
# ============================================================================
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("📚 Tesis IA - Análisis de Campañas")

with col2:
    st.caption("🔗 [Documentación](https://github.com)")

with col3:
    st.caption("📧 Contacto: tu_email@example.com")
