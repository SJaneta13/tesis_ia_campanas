# dashboard/sections/perfil_muestra.py
import pandas as pd
import streamlit as st
import plotly.express as px

from components import topbar, kpi_card


def find_first_existing_column(df: pd.DataFrame, candidates: list[str]):
    if df.empty:
        return None

    normalized = {c.lower().strip(): c for c in df.columns}

    for candidate in candidates:
        key = candidate.lower().strip()
        if key in normalized:
            return normalized[key]

    for col in df.columns:
        col_l = col.lower().strip()
        for candidate in candidates:
            if candidate.lower().strip() in col_l:
                return col

    return None


def empty_state(message: str):
    st.markdown(
        f"""
        <div class="empty-state">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def clean_category_series(series: pd.Series, default: str = "No especificado"):
    return (
        series.fillna(default)
        .astype(str)
        .str.strip()
        .replace("", default)
    )


def make_category_distribution(
    df: pd.DataFrame,
    col: str,
    label_name: str,
    order: list[str] | None = None,
) -> pd.DataFrame:
    if df.empty or not col or col not in df.columns:
        return pd.DataFrame(columns=[label_name, "Cantidad", "Porcentaje"])

    temp = clean_category_series(df[col])

    counts = temp.value_counts()

    if order:
        counts = counts.reindex(order).fillna(0).astype(int)
        counts = counts[counts > 0]

    out = counts.reset_index()
    out.columns = [label_name, "Cantidad"]

    total = out["Cantidad"].sum()

    if total == 0:
        return pd.DataFrame(columns=[label_name, "Cantidad", "Porcentaje"])

    out["Porcentaje"] = (out["Cantidad"] / total * 100).round(1)

    return out


def donut_chart(df: pd.DataFrame, names_col: str, values_col: str, height: int = 315):
    if df.empty:
        return None


    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        hole=0.52,
        color_discrete_sequence=[
            "#0f6fc9",
            "#7cc4f8",
            "#ff2d2d",
            "#2cb6a4",
            "#facc15",
        ],
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Cantidad: %{value}<br>"
            "Porcentaje: %{percent}<extra></extra>"
        ),
    )

    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=0, r=0, t=0, b=0),
        legend_title_text="",
        legend=dict(
            orientation="v",
            y=0.72,
            x=1.02,
            font=dict(size=11),
        ),
    )

    return fig


def horizontal_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    text_col: str = "Porcentaje",
    height: int = 320,
):
    if df.empty:
        return None

    plot_df = df.sort_values(x_col, ascending=True)

    fig = px.bar(
        plot_df,
        x=x_col,
        y=y_col,
        orientation="h",
        text=text_col,
        color=y_col,
        color_discrete_sequence=[
            "#0f6fc9",
            "#7cc4f8",
            "#2cb6a4",
            "#facc15",
            "#fb7185",
            "#94a3b8",
        ],
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Cantidad: %{x}<br>"
            "Porcentaje: %{text:.1f}%<extra></extra>"
        ),
    )

    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=0, r=35, t=5, b=5),
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        yaxis=dict(title=""),
        showlegend=False,
        font=dict(size=11),
    )

    return fig


def render_card_header(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="section-title-card">{title}</div>
        <div class="section-subtitle-card">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def render_perfil_muestra(survey_df: pd.DataFrame):
    n_survey = len(survey_df) if not survey_df.empty else 0

    topbar(
        title="Perfil de la muestra",
        subtitle=(
            "Caracterización de los participantes de la comunidad universitaria UCE "
            "que respondieron la encuesta sobre inteligencia artificial en campañas políticas digitales."
        ),
        pill_text=f"n = {n_survey:,} encuestas" if n_survey else "encuestas no cargadas",
    )

    if survey_df.empty:
        empty_state("No se encontraron datos de encuesta para construir el perfil de la muestra.")
        return

    # =========================================================
    # Columnas de la Sección 1 de la encuesta
    # =========================================================
    edad_col = find_first_existing_column(
        survey_df,
        [
            "¿Cuál es tu edad?",
            "edad",
            "rango de edad",
            "age",
        ],
    )

    genero_col = find_first_existing_column(
        survey_df,
        [
            "¿Cuál es tu género?",
            "genero",
            "género",
            "gender",
            "sexo",
        ],
    )

    rol_col = find_first_existing_column(
        survey_df,
        [
            "¿Cuál es su rol dentro de la Universidad Central del Ecuador?",
            "rol dentro de la universidad",
            "rol",
            "universidad central del ecuador",
        ],
    )

    facultad_col = find_first_existing_column(
        survey_df,
        [
            "¿A qué facultad o unidad académica pertenece?",
            "facultad",
            "unidad académica",
            "unidad academica",
        ],
    )

    quito_col = find_first_existing_column(
        survey_df,
        [
            "¿Reside actualmente en la ciudad de Quito?",
            "reside actualmente",
            "reside en quito",
            "quito",
            "residencia",
        ],
    )

    # =========================================================
    # KPI superiores
    # =========================================================
    total_vars = sum(
        [
            bool(edad_col),
            bool(genero_col),
            bool(rol_col),
            bool(facultad_col),
            bool(quito_col),
        ]
    )

    residentes_quito = 0
    if quito_col:
        residentes_quito = (
            clean_category_series(survey_df[quito_col])
            .str.lower()
            .isin(["sí", "si", "s"])
            .sum()
        )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Encuestas válidas",
            f"{n_survey:,}",
            "Registros procesados de la muestra",
            "blue",
        )

    with c2:
        kpi_card(
            "Variables detectadas",
            f"{total_vars}/5",
            "Campos de caracterización encontrados",
            "green",
        )

    with c3:
        kpi_card(
            "Residen en Quito",
            f"{residentes_quito:,}" if quito_col else "N/D",
            "Participantes que declararon residencia",
            "yellow",
        )

    with c4:
        kpi_card(
            "Ámbito",
            "UCE",
            "Comunidad universitaria encuestada",
            "blue",
        )

    st.markdown('<div class="profile-section-gap"></div>', unsafe_allow_html=True)

    # =========================================================
    # Edad + género
    # =========================================================
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True, key="card_pm_edad"):
            render_card_header(
                "Distribución por edad",
                "Rangos etarios declarados por los participantes.",
            )

            if edad_col:
                edad_order = ["18–24", "18-24", "25–34", "25-34", "35–44", "35-44", "45–54", "45-54", "55–64", "55-64"]
                edad_df = make_category_distribution(
                    survey_df,
                    edad_col,
                    "Edad",
                )

                fig = horizontal_bar_chart(
                    edad_df,
                    x_col="Cantidad",
                    y_col="Edad",
                    text_col="Porcentaje",
                    height=315,
                )

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                else:
                    empty_state("No existen datos suficientes para graficar edad.")
            else:
                empty_state("No se encontró la columna de edad.")

    with col2:
        with st.container(border=True, key="card_pm_genero"):
            render_card_header(
                "Distribución por género",
                "Composición de participantes según género declarado.",
            )

            if genero_col:
                genero_df = make_category_distribution(
                    survey_df,
                    genero_col,
                    "Género",
                    order=["Masculino", "Femenino", "Otros"],
                )

                fig = donut_chart(
                    genero_df,
                    names_col="Género",
                    values_col="Cantidad",
                    height=315,
                )

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                else:
                    empty_state("No existen datos suficientes para graficar género.")
            else:
                empty_state("No se encontró la columna de género.")

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    # =========================================================
    # Rol + residencia
    # =========================================================
    col3, col4 = st.columns(2, gap="large")

    with col3:
        with st.container(border=True, key="card_pm_rol"):
            render_card_header(
                "Rol dentro de la UCE",
                "Participación según vínculo institucional con la universidad.",
            )

            if rol_col:
                rol_df = make_category_distribution(
                    survey_df,
                    rol_col,
                    "Rol",
                    order=[
                        "Estudiante de pregrado",
                        "Estudiante de posgrado",
                        "Docente",
                        "Personal administrativo",
                    ],
                )

                fig = horizontal_bar_chart(
                    rol_df,
                    x_col="Cantidad",
                    y_col="Rol",
                    text_col="Porcentaje",
                    height=315,
                )

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                else:
                    empty_state("No existen datos suficientes para graficar el rol.")
            else:
                empty_state("No se encontró la columna de rol dentro de la UCE.")

    with col4:
        with st.container(border=True, key="card_pm_quito"):
            render_card_header(
                "Residencia en Quito",
                "Participantes que declararon residir actualmente en la ciudad de Quito.",
            )

            if quito_col:
                quito_df = make_category_distribution(
                    survey_df,
                    quito_col,
                    "Residencia en Quito",
                    order=["Sí", "Si", "No"],
                )

                fig = donut_chart(
                    quito_df,
                    names_col="Residencia en Quito",
                    values_col="Cantidad",
                    height=315,
                )

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                else:
                    empty_state("No existen datos suficientes para graficar residencia en Quito.")
            else:
                empty_state("No se encontró la columna de residencia en Quito.")

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    # =========================================================
    # Facultad
    # =========================================================
    with st.container(border=True, key="card_pm_facultad"):
        render_card_header(
            "Facultad o unidad académica",
            "Distribución de la muestra según la facultad o unidad de pertenencia.",
        )

        if facultad_col:
            facultad_df = make_category_distribution(
                survey_df,
                facultad_col,
                "Facultad o unidad",
            )

            fig = horizontal_bar_chart(
                facultad_df,
                x_col="Cantidad",
                y_col="Facultad o unidad",
                text_col="Porcentaje",
                height=520,
            )

            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                empty_state("No existen datos suficientes para graficar facultades.")
        else:
            empty_state("No se encontró la columna de facultad o unidad académica.")

    st.caption(
        "Nota metodológica: esta sección describe la composición de la muestra encuestada. "
        "Estos datos permiten contextualizar los resultados sobre conocimiento, percepción y confianza frente al uso de IA electoral."
    )