#!/bin/bash
# Script para ejecutar la interfaz Streamlit

# Activar el entorno virtual (Windows)
# source venv_scraping/Scripts/activate  # Para Linux/Mac
# .\venv_scraping\Scripts\activate  # Para Windows

# Ejecutar la aplicación Streamlit
streamlit run app.py --logger.level=debug

# Acceder en: http://localhost:8501
