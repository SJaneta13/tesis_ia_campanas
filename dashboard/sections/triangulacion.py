# dashboard/sections/triangulacion.py

import pandas as pd
import streamlit as st

from dashboard.components import topbar, kpi_card, method_card
from dashboard.common import (
    PLOTLY_CONFIG,
    empty_state,
    make_category_distribution,
    horizontal_bar_chart,
    render_card_header,
    render_note,
    safe_text,
)
from dashboard.data_loader import (
    load_triangulation_matrix,
    load_recommendation_rules,
)


def _safe_count(df: pd.DataFrame) -> int:
    if df is None or df.empty:
        return 0
    return len(df)


def _safe_value(row: pd.Series, col: str, default: str = "No disponible") -> str:
    if col not in row.index:
        return default

    value = row.get(col)

    if pd.isna(value) or str(value).strip() == "":
        return default

    return str(value).strip()


def _score_level(level: str) -> int:
    level = str(level).lower()

    if "fuerte" in level:
        return 3
    if "media" in level:
        return 2
    if "normativa" in level or "contextual" in level:
        return 2
    if "exploratoria" in level:
        return 1

    return 1


def _score_label(score: int) -> str:
    if score >= 3:
        return "Fuerte"
    if score == 2:
        return "Media"
    return "Exploratoria"


def _score_variant(score: int) -> str:
    if score >= 3:
        return "green"
    if score == 2:
        return "yellow"
    return "blue"


def _build_scores_df(triangulation_df: pd.DataFrame) -> pd.DataFrame:
    if triangulation_df is None or triangulation_df.empty:
        return pd.DataFrame(columns=["Dimensión", "Nivel", "Puntaje"])

    out = triangulation_df.copy()

    if "Nivel de triangulación" not in out.columns:
        out["Nivel de triangulación"] = "Exploratoria"

    out["Puntaje"] = out["Nivel de triangulación"].apply(_score_level)
    out["Nivel"] = out["Puntaje"].apply(_score_label)

    return out


def _render_score_distribution(scores_df: pd.DataFrame):
    if scores_df.empty:
        empty_state("No hay información suficiente para mostrar consistencia de evidencia.")
        return

    dist = make_category_distribution(
        scores_df,
        col="Nivel",
        label_name="Nivel",
        order=["Fuerte", "Media", "Exploratoria"],
    )

    fig = horizontal_bar_chart(
        dist,
        x_col="Cantidad",
        y_col="Nivel",
        text_col="Porcentaje",
        height=250,
    )

    if fig:
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        empty_state("No existen datos suficientes para graficar el nivel de triangulación.")


def _render_interpretation_summary(scores_df: pd.DataFrame):
    if scores_df.empty:
        empty_state("No hay datos suficientes para construir la lectura ejecutiva.")
        return

    total = len(scores_df)
    fuerte = int((scores_df["Nivel"] == "Fuerte").sum())
    media = int((scores_df["Nivel"] == "Media").sum())
    exploratoria = int((scores_df["Nivel"] == "Exploratoria").sum())

    fuerte_pct = fuerte / total * 100 if total else 0
    media_pct = media / total * 100 if total else 0
    exploratoria_pct = exploratoria / total * 100 if total else 0

    st.markdown(
        f"""
        <div class="interpretation-grid">
            <div class="interpretation-box green">
                <div class="interpretation-value">{fuerte}</div>
                <div class="interpretation-label">
                    dimensiones con evidencia fuerte ({fuerte_pct:.1f}% del total).
                </div>
            </div>
            <div class="interpretation-box yellow">
                <div class="interpretation-value">{media}</div>
                <div class="interpretation-label">
                    dimensiones con evidencia media o contextual ({media_pct:.1f}%).
                </div>
            </div>
            <div class="interpretation-box blue">
                <div class="interpretation-value">{exploratoria}</div>
                <div class="interpretation-label">
                    dimensiones exploratorias que requieren lectura prudente ({exploratoria_pct:.1f}%).
                </div>
            </div>
            <div class="interpretation-box red">
                <div class="interpretation-value">{total}</div>
                <div class="interpretation-label">
                    dimensiones analíticas cruzadas entre encuesta, evidencia digital y modelo.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_dimension_detail(row: pd.Series):
    dimension = _safe_value(row, "Dimensión")
    encuesta = _safe_value(row, "Evidencia de encuesta")
    digital = _safe_value(row, "Evidencia digital")
    modelo = _safe_value(row, "Evidencia de modelo")
    lectura = _safe_value(row, "Lectura para tesis")
    nivel = _safe_value(row, "Nivel de triangulación")

    score = _score_level(nivel)
    variant = _score_variant(score)

    render_card_header(
        dimension,
        f"Nivel de consistencia: {_score_label(score).lower()}."
    )

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        with st.container(border=True, key="card_tri_fuente_encuesta"):
            st.markdown("**Encuesta**")
            st.caption("Evidencia perceptual")
            render_note(encuesta, color="blue")

    with c2:
        with st.container(border=True, key="card_tri_fuente_digital"):
            st.markdown("**Evidencia digital**")
            st.caption("Contexto del ecosistema informativo")
            render_note(digital, color="yellow")

    with c3:
        with st.container(border=True, key="card_tri_fuente_modelo"):
            st.markdown("**Modelo exploratorio**")
            st.caption("Patrones analíticos no causales")
            render_note(modelo, color="green")

    render_note(
        f"Lectura integrada: {lectura}",
        color=variant,
    )


def _filter_recommendations(
    recommendation_rules: pd.DataFrame,
    selected_dimension: str,
) -> pd.DataFrame:
    if recommendation_rules is None or recommendation_rules.empty:
        return pd.DataFrame()

    dim = str(selected_dimension).lower()

    def row_text(row: pd.Series) -> str:
        return " ".join(row.astype(str)).lower()

    if "bot" in dim or "automatización" in dim:
        mask = recommendation_rules.apply(
            lambda row: "bot" in row_text(row) or "automatización" in row_text(row),
            axis=1,
        )

    elif "deepfake" in dim or "sintético" in dim:
        mask = recommendation_rules.apply(
            lambda row: (
                "deepfake" in row_text(row)
                or "sintético" in row_text(row)
                or "contenido" in row_text(row)
            ),
            axis=1,
        )

    elif "microsegmentación" in dim:
        mask = recommendation_rules.apply(
            lambda row: "microsegmentación" in row_text(row) or "segmentación" in row_text(row),
            axis=1,
        )

    elif "alfabetización" in dim:
        mask = recommendation_rules.apply(
            lambda row: (
                "alfabetización" in row_text(row)
                or "formativas" in row_text(row)
                or "verificación" in row_text(row)
            ),
            axis=1,
        )

    elif "regulación" in dim or "transparencia" in dim:
        mask = recommendation_rules.apply(
            lambda row: (
                "regulación" in row_text(row)
                or "transparencia" in row_text(row)
                or "trazabilidad" in row_text(row)
            ),
            axis=1,
        )

    else:
        mask = pd.Series([True] * len(recommendation_rules), index=recommendation_rules.index)

    filtered = recommendation_rules.loc[mask].copy()

    if filtered.empty:
        return recommendation_rules.head(3).copy()

    return filtered.head(3).copy()


def _render_recommendations(recommendation_df: pd.DataFrame):
    if recommendation_df is None or recommendation_df.empty:
        empty_state("No se encontraron recomendaciones para esta dimensión.")
        return

    for idx, row in recommendation_df.reset_index(drop=True).iterrows():
        condition = row.get("Condición analítica", "Condición no disponible")
        recommendation = row.get("Recomendación técnica", "Recomendación no disponible")
        actor = row.get("Actor sugerido", "Actor no definido")
        rec_type = row.get("Tipo", "General")

        with st.container(border=True, key=f"card_tri_rec_{idx}"):
            st.markdown(f"**{safe_text(condition)}**")
            st.caption(f"Tipo: {safe_text(rec_type)}")
            render_note(recommendation, color="blue")
            st.caption(f"Actor sugerido: {safe_text(actor)}")


def render_triangulacion(
    survey_df: pd.DataFrame,
    news_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
    active_filters: dict | None = None,
):
    n_survey = _safe_count(survey_df)
    n_news = _safe_count(news_df)
    n_metrics = _safe_count(metrics_df)

    topbar(
        title="Triangulación",
        subtitle=(
            "Contraste entre resultados de encuesta, evidencia digital pública y modelado predictivo "
            "para interpretar la relación entre inteligencia artificial y confianza electoral."
        ),
        pill_text=f"n = {n_survey:,} encuestas" if n_survey else "encuestas no cargadas",
    )

    triangulation_df = load_triangulation_matrix()
    recommendation_rules = load_recommendation_rules()

    if triangulation_df.empty:
        empty_state(
            "No se encontró la matriz de triangulación. Ejecuta el script de generación de artefactos."
        )
        return

    scores_df = _build_scores_df(triangulation_df)
    strong_count = int((scores_df["Nivel"] == "Fuerte").sum()) if not scores_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Encuestas filtradas",
            f"{n_survey:,}",
            "Comunidad universitaria UCE, 18 a 64 años",
            "blue",
        )

    with c2:
        kpi_card(
            "Evidencia digital",
            f"{n_news:,}",
            "Noticias/corpus contextual",
            "yellow",
        )

    with c3:
        kpi_card(
            "Dimensiones cruzadas",
            f"{len(triangulation_df):,}",
            "Ejes analíticos del estudio",
            "green",
        )

    with c4:
        kpi_card(
            "Evidencia fuerte",
            f"{strong_count}",
            "Coincidencia alta entre fuentes",
            "green" if strong_count else "red",
        )

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_tri_panorama"):
        render_card_header(
            "Panorama de triangulación",
            "La triangulación no sustituye los resultados descriptivos ni el modelo; los conecta para interpretar la consistencia de los hallazgos.",
        )
        _render_interpretation_summary(scores_df)

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        with st.container(border=True, key="card_tri_consistencia"):
            render_card_header(
                "Consistencia de evidencia",
                "Distribución del nivel de coincidencia entre encuesta, evidencia digital y modelo.",
            )
            _render_score_distribution(scores_df)

    with col2:
        with st.container(border=True, key="card_tri_resumen"):
            render_card_header(
                "Lectura ejecutiva",
                "Interpretación metodológica para el público del sistema.",
            )

            render_note(
                "La encuesta aporta la percepción ciudadana; el corpus digital contextualiza el entorno electoral; "
                "y el modelo identifica asociaciones exploratorias, no causales.",
                color="blue",
            )

            render_note(
                "Este módulo permite distinguir entre hallazgos fuertes, evidencia contextual y señales exploratorias.",
                color="green",
            )

            if n_survey < 30:
                render_note(
                    "La muestra filtrada es menor a 30 registros. Interpreta esta segmentación con cautela.",
                    color="yellow",
                )

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    tabs = st.tabs(
        [
            "Explorar dimensión",
            "Matriz técnica",
            "Recomendaciones",
        ]
    )

    dimensions = triangulation_df["Dimensión"].dropna().astype(str).tolist()
    selected_dimension = dimensions[0] if dimensions else ""

    with tabs[0]:
        with st.container(border=True, key="card_tri_dimension"):
            render_card_header(
                "Exploración por dimensión",
                "Seleccione un eje para revisar cómo se conectan encuesta, evidencia digital y modelo.",
            )

            f1, f2 = st.columns([1, 1], gap="medium")

            with f1:
                selected_level = st.selectbox(
                    "Filtrar por nivel de evidencia",
                    ["Todos", "Fuerte", "Media", "Exploratoria"],
                    key="tri_filter_level",
                )

            filtered_scores = scores_df.copy()

            if selected_level != "Todos":
                filtered_scores = filtered_scores[filtered_scores["Nivel"] == selected_level]

            filtered_dimensions = filtered_scores["Dimensión"].dropna().astype(str).tolist()

            if not filtered_dimensions:
                empty_state("No hay dimensiones disponibles para el filtro seleccionado.")
            else:
                with f2:
                    selected_dimension = st.selectbox(
                        "Dimensión de análisis",
                        filtered_dimensions,
                        key="tri_selected_dimension",
                    )

                selected_row = triangulation_df[
                    triangulation_df["Dimensión"].astype(str) == selected_dimension
                ].iloc[0]

                _render_dimension_detail(selected_row)

    with tabs[1]:
        with st.container(border=True, key="card_tri_matriz"):
            render_card_header(
                "Matriz técnica de triangulación",
                "Vista filtrable de las dimensiones analíticas, su nivel de evidencia y lectura integrada.",
            )

            m1, m2 = st.columns([1, 1], gap="medium")

            with m1:
                matrix_level = st.selectbox(
                    "Nivel",
                    ["Todos", "Fuerte", "Media", "Exploratoria"],
                    key="tri_matrix_level",
                )

            with m2:
                search_text = st.text_input(
                    "Buscar en dimensión o lectura",
                    placeholder="Ejemplo: bots, regulación, deepfakes...",
                    key="tri_matrix_search",
                )

            matrix_df = scores_df.copy()

            if matrix_level != "Todos":
                matrix_df = matrix_df[matrix_df["Nivel"] == matrix_level]

            if search_text.strip():
                search = search_text.lower().strip()
                matrix_df = matrix_df[
                    matrix_df.apply(
                        lambda row: search in " ".join(row.astype(str)).lower(),
                        axis=1,
                    )
                ]

            compact_cols = ["Dimensión", "Nivel", "Lectura para tesis"]
            compact_cols = [col for col in compact_cols if col in matrix_df.columns]

            compact_df = matrix_df[compact_cols].rename(
                columns={
                    "Lectura para tesis": "Lectura integrada",
                }
            )

            st.dataframe(
                compact_df,
                use_container_width=True,
                hide_index=True,
                height=300,
                column_config={
                    "Dimensión": st.column_config.TextColumn("Dimensión", width="medium"),
                    "Nivel": st.column_config.TextColumn("Nivel", width="small"),
                    "Lectura integrada": st.column_config.TextColumn("Lectura integrada", width="large"),
                },
            )

            with st.expander("Ver matriz completa"):
                st.dataframe(
                    triangulation_df,
                    use_container_width=True,
                    hide_index=True,
                    height=420,
                )

            csv = triangulation_df.to_csv(index=False, encoding="utf-8-sig")

            st.download_button(
                "Descargar matriz de triangulación",
                data=csv,
                file_name="triangulation_matrix.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_triangulation_matrix",
            )

    with tabs[2]:
        selected_recommendations = _filter_recommendations(
            recommendation_rules,
            selected_dimension,
        )

        with st.container(border=True, key="card_tri_recomendaciones"):
            render_card_header(
                "Recomendaciones derivadas",
                "Acciones técnicas, institucionales o académicas vinculadas con la dimensión seleccionada.",
            )

            if selected_dimension:
                render_note(
                    f"Dimensión activa: {selected_dimension}",
                    color="blue",
                )

            _render_recommendations(selected_recommendations)

            if not recommendation_rules.empty:
                csv = recommendation_rules.to_csv(index=False, encoding="utf-8-sig")

                st.download_button(
                    "Descargar reglas de recomendación",
                    data=csv,
                    file_name="recommendation_rules.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_recommendation_rules_tri",
                )

    st.caption(
        "Nota metodológica: la triangulación integra evidencia perceptual, evidencia digital contextual y patrones del modelado exploratorio. "
        "No establece causalidad ni generalización poblacional."
    )
