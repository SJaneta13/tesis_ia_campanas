# dashboard/sections/datos_artefactos.py

import pandas as pd
import streamlit as st

from dashboard.components import topbar, kpi_card, method_card
from dashboard.common import (
    PLOTLY_CONFIG,
    empty_state,
    make_category_distribution,
    horizontal_bar_chart,
    donut_chart,
    render_card_header,
    render_note,
)
from dashboard.data_loader import (
    load_data_quality_report,
    load_variable_dictionary,
    load_construct_map,
    load_recommendation_rules,
)


def _safe_count(df: pd.DataFrame) -> int:
    if df is None or df.empty:
        return 0
    return len(df)


def _quality_value(df: pd.DataFrame, indicador: str, default: str = "N/D"):
    if df is None or df.empty:
        return default

    if "Indicador" not in df.columns or "Valor" not in df.columns:
        return default

    mask = df["Indicador"].astype(str).str.lower().str.strip() == indicador.lower().strip()

    if not mask.any():
        return default

    return df.loc[mask, "Valor"].iloc[0]


def _download_button(df: pd.DataFrame, filename: str, label: str, key: str):
    if df is None or df.empty:
        return

    csv = df.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        label,
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
        key=key,
    )


def _render_construct_chart(variable_dictionary: pd.DataFrame):
    if variable_dictionary.empty or "Constructo asociado" not in variable_dictionary.columns:
        empty_state("No hay información suficiente para graficar constructos.")
        return

    dist = make_category_distribution(
        variable_dictionary,
        col="Constructo asociado",
        label_name="Constructo",
    )

    fig = horizontal_bar_chart(
        dist,
        x_col="Cantidad",
        y_col="Constructo",
        text_col="Porcentaje",
        height=310,
    )

    if fig:
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        empty_state("No existen datos suficientes para graficar constructos.")


def _render_type_chart(variable_dictionary: pd.DataFrame):
    if variable_dictionary.empty or "Tipo inferido" not in variable_dictionary.columns:
        empty_state("No hay información suficiente para graficar tipos de variables.")
        return

    dist = make_category_distribution(
        variable_dictionary,
        col="Tipo inferido",
        label_name="Tipo",
    )

    fig = donut_chart(
        dist,
        names_col="Tipo",
        values_col="Cantidad",
        height=310,
    )

    if fig:
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        empty_state("No existen datos suficientes para graficar tipos de variables.")


def _render_artifact_downloads(
    data_quality: pd.DataFrame,
    variable_dictionary: pd.DataFrame,
    construct_map: pd.DataFrame,
    recommendation_rules: pd.DataFrame,
):
    artifacts = [
        {
            "title": "Reporte de calidad de datos",
            "description": "Resume registros, columnas, completitud, duplicados y variables clave de la base procesada.",
            "filename": "data_quality_report.csv",
            "df": data_quality,
            "key": "download_artifact_quality",
        },
        {
            "title": "Diccionario de variables",
            "description": "Documenta tipo inferido, constructo asociado y uso analítico de cada variable.",
            "filename": "variable_dictionary.csv",
            "df": variable_dictionary,
            "key": "download_artifact_dictionary",
        },
        {
            "title": "Mapa de operacionalización",
            "description": "Relaciona constructos teóricos, variables esperadas, módulo de la plataforma y uso metodológico.",
            "filename": "construct_map.csv",
            "df": construct_map,
            "key": "download_artifact_construct_map",
        },
        {
            "title": "Reglas de recomendación",
            "description": "Define condiciones analíticas y recomendaciones técnicas, institucionales o académicas.",
            "filename": "recommendation_rules.csv",
            "df": recommendation_rules,
            "key": "download_artifact_recommendations",
        },
    ]

    cols = st.columns(2, gap="medium")

    for idx, artifact in enumerate(artifacts):
        with cols[idx % 2]:
            with st.container(border=True, key=f"card_art_download_{idx}"):
                method_card(
                    artifact["title"],
                    artifact["description"],
                )

                if artifact["df"] is None or artifact["df"].empty:
                    render_note(
                        f"Artefacto pendiente: {artifact['filename']}",
                        color="yellow",
                    )
                else:
                    render_note(
                        f"Disponible: {artifact['filename']}",
                        color="green",
                    )

                    _download_button(
                        artifact["df"],
                        artifact["filename"],
                        f"Descargar {artifact['title'].lower()}",
                        key=artifact["key"],
                    )


def _render_quality_summary(data_quality: pd.DataFrame):
    if data_quality.empty:
        empty_state("No hay reporte de calidad disponible.")
        return

    registros = _quality_value(data_quality, "Registros válidos cargados", "N/D")
    variables = _quality_value(data_quality, "Variables disponibles", "N/D")
    completitud = _quality_value(data_quality, "Completitud general de la base (%)", "N/D")
    duplicados = _quality_value(data_quality, "Registros duplicados exactos", "N/D")

    st.markdown(
        f"""
        <div class="interpretation-grid">
            <div class="interpretation-box blue">
                <div class="interpretation-value">{registros}</div>
                <div class="interpretation-label">
                    registros válidos cargados en la base procesada.
                </div>
            </div>
            <div class="interpretation-box green">
                <div class="interpretation-value">{variables}</div>
                <div class="interpretation-label">
                    variables disponibles para análisis y visualización.
                </div>
            </div>
            <div class="interpretation-box yellow">
                <div class="interpretation-value">{completitud}%</div>
                <div class="interpretation-label">
                    completitud general estimada en la base de datos.
                </div>
            </div>
            <div class="interpretation-box red">
                <div class="interpretation-value">{duplicados}</div>
                <div class="interpretation-label">
                    registros duplicados exactos identificados.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_datos_artefactos(
    survey_df: pd.DataFrame,
    survey_df_filtered: pd.DataFrame,
    news_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
):
    n_survey = _safe_count(survey_df)
    n_filtered = _safe_count(survey_df_filtered)
    n_news = _safe_count(news_df)
    n_metrics = _safe_count(metrics_df)

    topbar(
        title="Datos y artefactos",
        subtitle=(
            "Trazabilidad del sistema analítico: calidad de datos, diccionario de variables, "
            "operacionalización y archivos reproducibles de la plataforma."
        ),
        pill_text="Reproducibilidad",
    )

    data_quality = load_data_quality_report()
    variable_dictionary = load_variable_dictionary()
    construct_map = load_construct_map()
    recommendation_rules = load_recommendation_rules()

    completeness = _quality_value(data_quality, "Completitud general de la base (%)")
    duplicated = _quality_value(data_quality, "Registros duplicados exactos")

    available_artifacts = sum(
        [
            not data_quality.empty,
            not variable_dictionary.empty,
            not construct_map.empty,
            not recommendation_rules.empty,
        ]
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Base procesada",
            f"{n_survey:,}",
            "Registros válidos cargados",
            "blue",
        )

    with c2:
        kpi_card(
            "Muestra filtrada",
            f"{n_filtered:,}",
            "Segmento activo según filtros",
            "green",
        )

    with c3:
        kpi_card(
            "Completitud",
            f"{completeness}%" if completeness != "N/D" else "N/D",
            "Porcentaje de celdas no vacías",
            "yellow",
        )

    with c4:
        kpi_card(
            "Artefactos",
            f"{available_artifacts}/4",
            "Archivos técnicos disponibles",
            "blue" if available_artifacts == 4 else "red",
        )

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_art_resumen"):
        render_card_header(
            "Resumen técnico del sistema",
            "Este módulo documenta la trazabilidad de la plataforma y permite verificar la base de datos, variables, constructos y artefactos reproducibles.",
        )

        _render_quality_summary(data_quality)

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(border=True, key="card_art_constructos"):
            render_card_header(
                "Variables por constructo",
                "Distribución de variables según su función metodológica dentro del estudio.",
            )
            _render_construct_chart(variable_dictionary)

    with col2:
        with st.container(border=True, key="card_art_tipos"):
            render_card_header(
                "Tipos de variables",
                "Clasificación técnica inferida de las columnas disponibles en la base procesada.",
            )
            _render_type_chart(variable_dictionary)

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    tabs = st.tabs(
        [
            "Calidad de datos",
            "Diccionario",
            "Operacionalización",
            "Descargas",
        ]
    )

    with tabs[0]:
        with st.container(border=True, key="card_art_calidad"):
            render_card_header(
                "Reporte de calidad de datos",
                "Resumen de consistencia, completitud y estructura de la base utilizada por la plataforma.",
            )

            if data_quality.empty:
                empty_state(
                    "No se encontró data_quality_report.csv. Ejecuta el script generador de artefactos."
                )
            else:
                quality_cols = ["Indicador", "Valor", "Interpretación"]
                quality_cols = [col for col in quality_cols if col in data_quality.columns]

                st.dataframe(
                    data_quality[quality_cols],
                    use_container_width=True,
                    hide_index=True,
                    height=300,
                    column_config={
                        "Indicador": st.column_config.TextColumn("Indicador", width="medium"),
                        "Valor": st.column_config.TextColumn("Valor", width="small"),
                        "Interpretación": st.column_config.TextColumn("Interpretación", width="large"),
                    },
                )

                if str(duplicated) not in ["0", "0.0", "N/D"]:
                    render_note(
                        "Existen registros duplicados exactos. Revisa si corresponden a respuestas repetidas o registros válidos.",
                        color="yellow",
                    )
                else:
                    render_note(
                        "La base procesada no reporta duplicados exactos en el artefacto de calidad.",
                        color="green",
                    )

                if n_filtered < 30:
                    render_note(
                        "La muestra filtrada es menor a 30 registros. Las lecturas segmentadas deben interpretarse con cautela.",
                        color="yellow",
                    )

                _download_button(
                    data_quality,
                    "data_quality_report.csv",
                    "Descargar reporte de calidad",
                    "download_quality_report_tab",
                )

    with tabs[1]:
        with st.container(border=True, key="card_art_diccionario"):
            render_card_header(
                "Diccionario técnico de variables",
                "Relación entre columnas, constructos, tipo inferido y uso dentro de la plataforma.",
            )

            if variable_dictionary.empty:
                empty_state("No se encontró variable_dictionary.csv.")
            else:
                filter_col1, filter_col2 = st.columns([1, 1], gap="medium")

                construct_options = ["Todos"]
                use_options = ["Todos"]

                if "Constructo asociado" in variable_dictionary.columns:
                    construct_options += sorted(
                        variable_dictionary["Constructo asociado"]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )

                if "Uso en la plataforma" in variable_dictionary.columns:
                    use_options += sorted(
                        variable_dictionary["Uso en la plataforma"]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )

                with filter_col1:
                    selected_construct = st.selectbox(
                        "Filtrar por constructo",
                        construct_options,
                        key="art_construct_filter",
                    )

                with filter_col2:
                    selected_use = st.selectbox(
                        "Filtrar por uso",
                        use_options,
                        key="art_use_filter",
                    )

                search_variable = st.text_input(
                    "Buscar variable",
                    placeholder="Ejemplo: confianza, edad, bots, IA...",
                    key="art_variable_search",
                )

                filtered_dict = variable_dictionary.copy()

                if selected_construct != "Todos" and "Constructo asociado" in filtered_dict.columns:
                    filtered_dict = filtered_dict[
                        filtered_dict["Constructo asociado"].astype(str) == selected_construct
                    ]

                if selected_use != "Todos" and "Uso en la plataforma" in filtered_dict.columns:
                    filtered_dict = filtered_dict[
                        filtered_dict["Uso en la plataforma"].astype(str) == selected_use
                    ]

                if search_variable.strip():
                    search = search_variable.lower().strip()
                    filtered_dict = filtered_dict[
                        filtered_dict.apply(
                            lambda row: search in " ".join(row.astype(str)).lower(),
                            axis=1,
                        )
                    ]

                compact_cols = [
                    "Variable",
                    "Constructo asociado",
                    "Uso en la plataforma",
                    "Tipo inferido",
                ]

                compact_cols = [col for col in compact_cols if col in filtered_dict.columns]

                st.dataframe(
                    filtered_dict[compact_cols],
                    use_container_width=True,
                    hide_index=True,
                    height=390,
                    column_config={
                        "Variable": st.column_config.TextColumn("Variable", width="large"),
                        "Constructo asociado": st.column_config.TextColumn("Constructo", width="medium"),
                        "Uso en la plataforma": st.column_config.TextColumn("Uso", width="medium"),
                        "Tipo inferido": st.column_config.TextColumn("Tipo", width="small"),
                    },
                )

                with st.expander("Ver diccionario completo con conteos"):
                    st.dataframe(
                        variable_dictionary,
                        use_container_width=True,
                        hide_index=True,
                        height=460,
                    )

                _download_button(
                    variable_dictionary,
                    "variable_dictionary.csv",
                    "Descargar diccionario de variables",
                    "download_variable_dictionary_tab",
                )

    with tabs[2]:
        with st.container(border=True, key="card_art_operacionalizacion"):
            render_card_header(
                "Mapa de operacionalización",
                "Conexión entre marco teórico, variables esperadas, módulo de análisis y uso metodológico.",
            )

            if construct_map.empty:
                empty_state("No se encontró construct_map.csv.")
            else:
                module_options = ["Todos"]

                if "Módulo" in construct_map.columns:
                    module_options += sorted(
                        construct_map["Módulo"]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )

                selected_module = st.selectbox(
                    "Filtrar por módulo",
                    module_options,
                    key="art_module_filter",
                )

                filtered_map = construct_map.copy()

                if selected_module != "Todos" and "Módulo" in filtered_map.columns:
                    filtered_map = filtered_map[
                        filtered_map["Módulo"].astype(str) == selected_module
                    ]

                compact_cols = [
                    "Constructo teórico",
                    "Variable esperada",
                    "Módulo",
                    "Uso metodológico",
                ]

                compact_cols = [col for col in compact_cols if col in filtered_map.columns]

                st.dataframe(
                    filtered_map[compact_cols],
                    use_container_width=True,
                    hide_index=True,
                    height=360,
                    column_config={
                        "Constructo teórico": st.column_config.TextColumn("Constructo", width="medium"),
                        "Variable esperada": st.column_config.TextColumn("Variable esperada", width="medium"),
                        "Módulo": st.column_config.TextColumn("Módulo", width="medium"),
                        "Uso metodológico": st.column_config.TextColumn("Uso metodológico", width="large"),
                    },
                )

                render_note(
                    "Este mapa justifica que cada módulo de la plataforma responde a un constructo teórico, una variable analítica y un uso metodológico concreto.",
                    color="blue",
                )

                _download_button(
                    construct_map,
                    "construct_map.csv",
                    "Descargar mapa de operacionalización",
                    "download_construct_map_tab",
                )

    with tabs[3]:
        with st.container(border=True, key="card_art_descargas"):
            render_card_header(
                "Artefactos reproducibles",
                "Archivos técnicos que documentan la trazabilidad del análisis y respaldan la defensa del sistema.",
            )

            _render_artifact_downloads(
                data_quality,
                variable_dictionary,
                construct_map,
                recommendation_rules,
            )

            render_note(
                "Estos artefactos permiten defender la plataforma como producto técnico de Sistemas de Información porque documentan datos, variables, operacionalización y reglas analíticas.",
                color="green",
            )

    st.caption(
        "Nota metodológica: la población de análisis corresponde a la comunidad universitaria de la UCE entre 18 y 64 años. "
        "Los artefactos se utilizan para trazabilidad, reproducibilidad y documentación del sistema analítico."
    )
