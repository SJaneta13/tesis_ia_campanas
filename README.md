# Dashboard de tesis · IA y campañas políticas digitales 2025

## Descripción del proyecto

Este repositorio contiene el dashboard analítico desarrollado como parte del trabajo de titulación de la carrera de **Sistemas de Información** de la **Universidad Central del Ecuador**.

El proyecto analiza la percepción ciudadana sobre el uso de inteligencia artificial en campañas políticas digitales, tomando como caso de estudio el proceso electoral presidencial ecuatoriano de 2025. El dashboard integra resultados de encuesta, análisis descriptivo, evidencia digital contextual y modelos predictivos exploratorios para apoyar la interpretación académica de los hallazgos.

La plataforma fue desarrollada en **Python** con **Streamlit**, utilizando procesamiento de datos, visualización interactiva y modelos de aprendizaje automático como componentes de apoyo al análisis.

---

## Tema de investigación

**Análisis de la percepción ciudadana sobre el uso de inteligencia artificial en campañas políticas digitales en Quito: elecciones presidenciales de Ecuador 2025.**

---

## Objetivo general

Analizar la percepción, conocimiento y nivel de confianza electoral de la comunidad universitaria frente al uso de inteligencia artificial en campañas políticas digitales, mediante encuestas estructuradas, análisis de datos, evidencia digital contextual y modelado predictivo exploratorio.

---

## Alcance del dashboard

El dashboard permite explorar los principales resultados del estudio mediante módulos temáticos:

1. **Resumen general**
   Presenta los indicadores principales del estudio, hipótesis, perfil general de la muestra y síntesis metodológica.

2. **Perfil de la muestra**
   Describe la composición de los participantes por edad, género, rol dentro de la UCE y unidad académica.

3. **Conocimiento de IA**
   Analiza el conocimiento declarado, reconocimiento de automatización, capacidad percibida para identificar IA y exposición a contenido sospechoso.

4. **Percepción ciudadana**
   Examina actitudes frente al uso de IA en campañas políticas digitales: aceptación funcional, riesgo percibido, desconfianza digital y demanda de regulación.

5. **Confianza electoral**
   Presenta indicadores relacionados con confianza institucional, percepción de fraude o manipulación, influencia de IA en la decisión de voto y reducción de confianza frente a bots, deepfakes o contenido manipulado.

6. **Modelos predictivos**
   Incluye comparación de algoritmos, validación entre configuraciones de 3 y 5 niveles, matriz de confusión, importancia de variables, estabilidad por semilla y simulador exploratorio basado en Random Forest.

7. **Evidencia digital y triangulación**
   Integra los resultados de encuesta con evidencia digital externa proveniente de GDELT, medios digitales y registros sociales procesados, con fines contextuales y no causales.

8. **Datos y artefactos**
   Presenta trazabilidad de archivos procesados, artefactos utilizados y elementos de reproducibilidad del dashboard.

---

## Enfoque metodológico

El estudio sigue un enfoque **cuantitativo, descriptivo-exploratorio, observacional, no experimental y transversal**.

La fuente principal de información corresponde a una encuesta aplicada a participantes de la comunidad universitaria de la Universidad Central del Ecuador. La evidencia digital externa se utiliza como complemento contextual para observar señales del ecosistema informativo electoral, sin reemplazar la encuesta ni establecer causalidad.

El componente predictivo se desarrolló bajo una lógica exploratoria inspirada en el proceso **CRISP-DM**, considerando etapas de comprensión del problema, preparación de datos, modelado, evaluación e implementación visual en dashboard.

---

## Hipótesis del estudio

### H1 · Exposición digital y confianza electoral

A mayor exposición percibida a contenidos generados o potenciados por inteligencia artificial, menor nivel de confianza electoral en la comunidad universitaria analizada.

### H2 · Verificación informativa

La alfabetización mediática y la práctica de verificación informativa pueden moderar la relación entre exposición digital y confianza electoral, reduciendo la disminución de confianza frente a bots, deepfakes o microsegmentación política.

---

## Tecnologías utilizadas

* Python
* Streamlit
* Pandas
* NumPy
* Plotly
* Scikit-learn
* Joblib
* OpenPyXL
* HTML/CSS personalizado para el diseño visual del dashboard

---

## Estructura general del repositorio

```text
tesis_ia_campanas/
├── dashboard/
│   ├── app.py
│   ├── styles.py
│   ├── components.py
│   ├── common.py
│   ├── data_loader.py
│   ├── filters.py
│   ├── model_backend.py
│   └── sections/
│       ├── resumen_general.py
│       ├── perfil_muestra.py
│       ├── conocimiento_ia.py
│       ├── percepcion_ciudadana.py
│       ├── confianza_electoral.py
│       ├── modelos_predictivos.py
│       ├── evidencia_gdelt.py
│       └── datos_artefactos.py
│
├── data/
│   └── processed/
│       └── encuestas/
│           └── model_ready.csv
│
├── outputs/
│   ├── latest/
│   │   └── tables/
│   │       ├── model_metrics_summary.csv
│   │       ├── model_metrics_by_seed_dashboard.csv
│   │       ├── feature_importance_latest.csv
│   │       ├── confusion_matrix_3_levels.csv
│   │       ├── confusion_matrix_5_levels.csv
│   │       ├── simulator_feature_schema.csv
│   │       ├── simulator_defaults_5niveles.json
│   │       ├── model_metadata_5niveles.json
│   │       └── model_classes_5niveles.json
│   │
│   └── text_analysis/
│       ├── case1_es/
│       ├── case2_en/
│       └── case3_ec_media/
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Instalación local

Clonar el repositorio:

```bash
git clone https://github.com/USUARIO/NOMBRE_DEL_REPOSITORIO.git
cd NOMBRE_DEL_REPOSITORIO
```

Crear entorno virtual:

```bash
python -m venv .venv
```

Activar entorno virtual en Windows:

```bash
.venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar el dashboard:

```bash
streamlit run dashboard/app.py
```

---

## Despliegue en Streamlit Cloud

Para desplegar el dashboard en Streamlit Community Cloud, configurar:

```text
Repository: USUARIO/NOMBRE_DEL_REPOSITORIO
Branch: main
Main file path: dashboard/app.py
```

El archivo `requirements.txt` debe estar en la raíz del repositorio para que Streamlit instale correctamente las dependencias.

---

## Archivos necesarios para funcionamiento en la nube

El dashboard requiere que estén versionados los archivos procesados y artefactos finales usados en visualización:

```text
data/processed/encuestas/model_ready.csv
outputs/latest/tables/*.csv
outputs/latest/tables/*.json
outputs/latest/tables/*.joblib
outputs/text_analysis/*/news_sentiment_scored.csv
```

Los datos crudos, credenciales, cookies, entornos virtuales y archivos temporales no deben subirse al repositorio.

---

## Consideraciones éticas y metodológicas

Los resultados del dashboard deben interpretarse como evidencia descriptiva y exploratoria. La encuesta constituye la fuente principal del análisis, mientras que la evidencia digital externa se utiliza con fines contextuales.

El modelado predictivo no establece causalidad ni predice de forma determinística el comportamiento electoral individual. Su propósito es identificar patrones asociados a niveles de confianza electoral y apoyar la interpretación académica del estudio.

La evidencia digital no constituye una verificación forense de contenidos ni una auditoría de plataformas. Su función es complementar la lectura del entorno informativo electoral mediante registros disponibles y procesados.

---

## Limitaciones

* La muestra corresponde a participantes de la comunidad universitaria UCE y no representa proporcionalmente a toda la población ecuatoriana.
* El diseño de investigación es transversal, por lo que no permite inferir causalidad temporal.
* Los modelos predictivos son exploratorios y dependen de la calidad, distribución y tamaño de la muestra.
* La evidencia digital externa permite contextualizar el fenómeno, pero no prueba impacto directo sobre la confianza electoral.
* Los registros sociales procesados dependen de disponibilidad previa y no implican scraping directo o representatividad total de plataformas.

---

## Autores

**Silvia Janeta**
**Cristian Toca**

Carrera de Sistemas de Información
Universidad Central del Ecuador

Tutor: **Ing. Paulo Llaguno**

---

## Estado del proyecto

Dashboard académico desarrollado como producto de apoyo para el trabajo de titulación. La plataforma integra análisis descriptivo, visualización interactiva, evidencia digital contextual y modelado predictivo exploratorio para sustentar los resultados de la investigación.
