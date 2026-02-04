# 🚀 Interfaz Intuitiva - Análisis IA Campañas

Una interfaz moderna y fácil de usar construida con **Streamlit** para visualizar y explorar los análisis de campañas con inteligencia artificial.

## 📋 Características

✅ **Dashboard intuitivo** con métricas principales  
✅ **Análisis de sentimiento** con filtros interactivos  
✅ **Modelado de tópicos** con LDA  
✅ **Comparación de modelos ML** (Random Forest, SVM)  
✅ **Comparación entre casos** (España, Internacional, Ecuador)  
✅ **Configuración personalizable**  
✅ **Gráficos interactivos** con Plotly  

## 🛠️ Instalación

### Requisitos Previos
- Python 3.11+
- pip (gestor de paquetes)

### Paso 1: Instalar Dependencias
```bash
pip install -r requirements.txt
pip install streamlit plotly
```

### Paso 2: Ejecutar la Interfaz

**En Windows (PowerShell):**
```powershell
.\venv_scraping\Scripts\activate
streamlit run app.py
```

**En Linux/Mac:**
```bash
source venv_scraping/Scripts/activate
streamlit run app.py
```

## 📊 Estructura de Navegación

```
┌─ 📈 Dashboard
│  └─ Métricas clave, gráficos generales
│
├─ 💬 Análisis de Sentimiento
│  └─ Distribución de sentimientos, filtros por caso y tipo
│
├─ 📚 Modelado de Tópicos
│  └─ Tópicos principales, palabras clave
│
├─ 🤖 Modelos ML
│  └─ Performance de modelos, matrices de confusión
│
├─ 📊 Comparación de Casos
│  └─ Contraste entre España, Internacional y Ecuador
│
└─ ⚙️ Configuración
   └─ Directorios, tema, sincronización de datos
```

## 🎯 Cómo Usar

1. **Abre el navegador** en `http://localhost:8501`
2. **Navega** usando la barra lateral izquierda
3. **Interactúa** con los gráficos:
   - Hover para ver detalles
   - Click para ampliar/reducir
   - Descarga los gráficos como PNG

## 📁 Integración con Datos

Actualiza los datos en el código:

```python
# En app.py, busca las secciones de datos y reemplaza con:
df = pd.read_csv('data/processed/social_sentiment.csv')
# Luego visualiza con:
st.dataframe(df)
```

## 🎨 Personalización

### Cambiar Colores
```python
color_discrete_map={
    'Positivo': '#2ecc71',  # Verde
    'Neutral': '#f39c12',   # Naranja
    'Negativo': '#e74c3c'   # Rojo
}
```

### Agregar Nueva Página
```python
pages = {
    "📊 Dashboard": "dashboard",
    "🆕 Mi Nueva Página": "nueva_pagina",  # Agregar aquí
}

if page == "nueva_pagina":
    st.title("Mi Nueva Página")
    # Tu contenido aquí
```

## 📈 Ejemplos de Uso

### Filtrar Sentimientos
```python
sentiment_filter = st.multiselect(
    "Selecciona sentimientos:",
    ["Positivo", "Neutral", "Negativo"]
)
df_filtered = df[df['sentiment'].isin(sentiment_filter)]
```

### Crear Gráfico Interactivo
```python
fig = px.bar(df, x='categoria', y='cantidad',
            title='Mi Gráfico',
            color_discrete_sequence=['#3498db'])
st.plotly_chart(fig, use_container_width=True)
```

## 🔗 Conexión con Backend FastAPI

Actualizar `backend/app/main.py` para servir datos:

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse
import pandas as pd

@app.get("/api/sentiment")
def get_sentiment_data():
    df = pd.read_csv('outputs/latest/news_sentiment_scored.csv')
    return df.to_dict(orient='records')

@app.get("/api/topics")
def get_topics():
    with open('outputs/latest/news_topics_lda.csv') as f:
        return f.read()
```

Luego en `app.py`:
```python
import requests

@st.cache_data
def load_sentiment_data():
    response = requests.get('http://localhost:8000/api/sentiment')
    return pd.DataFrame(response.json())
```

## 🚀 Despliegue

### En Streamlit Cloud (Gratis)
1. Sube a GitHub
2. Ve a `streamlit.io`
3. Conecta tu repositorio
4. Listo!

### En tu propio servidor
```bash
# Instalar Streamlit en servidor
pip install streamlit

# Ejecutar con gunicorn
gunicorn -w 4 -b 0.0.0.0:8501 'streamlit.server.server:run_app'
```

## 📝 Notas

- Los datos mostrados son de ejemplo. Actualiza con tus CSV reales
- Las métricas se pueden enlazar a funciones que cargan datos vivos
- La caché de Streamlit (`@st.cache_data`) acelera las cargas

## 🆘 Solución de Problemas

**Error: ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**Puerto 8501 ocupado**
```bash
streamlit run app.py --server.port=8502
```

**Gráficos no se muestran**
```bash
pip install --upgrade plotly
```

## 📚 Recursos

- [Documentación Streamlit](https://docs.streamlit.io)
- [Plotly Documentación](https://plotly.com/python)
- [Streamlit Gallery](https://streamlit.io/gallery)

---

**¡Diviértete explorando tus datos!** 🎉
