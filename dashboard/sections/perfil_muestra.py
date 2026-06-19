# dashboard/sections/perfil_muestra.py
import pandas as pd
import streamlit as st

from dashboard.components import topbar, kpi_card
from dashboard.common import (
    PLOTLY_CONFIG,
    find_first_existing_column,
    empty_state,
    clean_category_series,
    make_category_distribution,
    donut_chart,
    horizontal_bar_chart,
    render_card_header,
)




def normalize_age_range(value):
    text = str(value).strip()
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace(" ", "")
    return text


def normalize_yes_no(value):
    text = str(value).strip().lower()
    text = text.replace("í", "i")

    if text in ["si", "s", "sí"]:
        return "Sí"
    if text in ["no", "n"]:
        return "No"

    return str(value).strip() or "No especificado"

def short_faculty_label(value: str) -> str:
    text = str(value).strip()

    replacements = {
        "Facultad de Ingeniería y Ciencias Aplicadas": "Ingeniería Aplicadas",
        "Facultad de Ciencias Administrativas": "Ciencias Administrativas",
        "Facultad de Ingeniería en Geología, Minas, Petróleos y Ambiental": "Geología Minas",
        "Facultad de Filosofía, Letras y Ciencias de la Educación": "Filosofía Educación",
        "Facultad de Comunicación Social": "Comunicación Social",
        "Facultad de Ciencias Económicas": "Ciencias Económicas",
        "Facultad de Ciencias Psicológicas": "Ciencias Psicológicas",
        "Facultad de Jurisprudencia, Ciencias Políticas y Sociales": "Jurisprudencia Política",
        "Facultad de Arquitectura y Urbanismo": "Arquitectura Urbanismo",
        "Facultad de Derecho": "Derecho",
        "Facultad de Odontología": "Odontología",
        "Facultad de Cultura Física": "Cultura Física",
        "Facultad de Ciencias Químicas": "Ciencias Químicas",
        "Facultad de Ciencias Agrícolas": "Ciencias Agrícolas",
        "Centro de Investigación": "Investigación",
        "Facultad de Artes": "Artes",
        "Facultad de Ciencias Biológicas": "Ciencias Biológicas",
        "Instituto de Posgrado": "Posgrado",
        "No pertenece a ninguna facultad / área administrativa": "Área administrativa",
        "Facultad de Ciencias Médicas": "Ciencias Médicas",
        "Enfermería": "Enfermería",
        "Facultad de Ciencias de la Discapacidad": "Discapacidad",
    }

    if text in replacements:
        return replacements[text]

    text = text.replace("Facultad de ", "")
    text = text.replace("Facultad del ", "")
    text = text.replace("Facultad ", "")
    text = text.replace("Ciencias de la ", "")
    text = text.replace("Ciencias del ", "")

    words = [w for w in text.split() if w.lower() not in ["de", "la", "las", "los", "y", "en"]]

    return " ".join(words[:2]) if words else "No registrado"

def collapse_top_categories(
    df: pd.DataFrame,
    label_col: str,
    top_n: int = 8,
    other_label: str = "Otras unidades",
) -> pd.DataFrame:
    if df is None or df.empty or label_col not in df.columns or "Cantidad" not in df.columns:
        return pd.DataFrame(columns=[label_col, "Cantidad", "Porcentaje"])

    temp = df.copy()
    temp["Cantidad"] = pd.to_numeric(temp["Cantidad"], errors="coerce").fillna(0).astype(int)
    temp = temp.sort_values("Cantidad", ascending=False)

    if len(temp) <= top_n:
        return temp.sort_values("Cantidad", ascending=True)

    top = temp.head(top_n).copy()
    rest = temp.iloc[top_n:].copy()

    total = temp["Cantidad"].sum()
    other_count = int(rest["Cantidad"].sum())

    other_row = pd.DataFrame(
        {
            label_col: [other_label],
            "Cantidad": [other_count],
            "Porcentaje": [round(other_count / total * 100, 1) if total else 0.0],
        }
    )

    out = pd.concat([top, other_row], ignore_index=True)
    return out.sort_values("Cantidad", ascending=True)

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
            "Rango etario",
            "18–64",
            "Participantes dentro del criterio de inclusión",
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

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # =========================================================
    # Edad + género
    # =========================================================
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(border=True, key="card_pm_edad"):
            render_card_header(
                "Distribución por edad",
                "Rangos etarios declarados por los participantes.",
            )

            if edad_col:
                edad_order = ["18-24", "25-34", "35-44", "45-54", "55-64"]


                edad_temp = survey_df.copy()
                edad_temp[edad_col] = edad_temp[edad_col].apply(normalize_age_range)

                edad_df = make_category_distribution(
                    edad_temp,
                    edad_col,
                    "Edad",
                    order=edad_order,
                )

                fig = horizontal_bar_chart(
                    edad_df,
                    x_col="Cantidad",
                    y_col="Edad",
                    text_col="Porcentaje",
                    height=315,
                )    

                if fig:
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
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
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    empty_state("No existen datos suficientes para graficar género.")
            else:
                empty_state("No se encontró la columna de género.")

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # =========================================================
    # Rol + residencia
    # =========================================================
    col3, col4 = st.columns([0.82, 1.35], gap="medium")

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
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    empty_state("No existen datos suficientes para graficar el rol.")
            else:
                empty_state("No se encontró la columna de rol dentro de la UCE.")

    with col4:
        with st.container(border=True, key="card_pm_facultad"):
            render_card_header(
                "Unidad académica",
                "Principales unidades representadas en la muestra.",
            )

            if facultad_col:
                facultad_df = make_category_distribution(
                    survey_df,
                    facultad_col,
                    "Facultad",
                )

                if facultad_df.empty:
                    empty_state("No existen datos suficientes para graficar unidades académicas.")
                else:
                    facultad_df = facultad_df.sort_values("Cantidad", ascending=False)

                    facultad_plot_df = collapse_top_categories(
                        facultad_df,
                        label_col="Facultad",
                        top_n=8,
                        other_label="Otras unidades",
                    )

                    facultad_plot_df["Unidad"] = facultad_plot_df["Facultad"].apply(short_faculty_label)

                    fig = horizontal_bar_chart(
                        facultad_plot_df,
                        x_col="Cantidad",
                        y_col="Unidad",
                        text_col="Porcentaje",
                        height=315,
                    )

                    if fig:
                        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                    else:
                        empty_state("No existen datos suficientes para graficar unidades académicas.")
            else:
                empty_state("No se encontró la columna de facultad o unidad académica.")

    if facultad_col:
        facultad_full_df = make_category_distribution(
            survey_df,
            facultad_col,
            "Facultad",
        )

        if not facultad_full_df.empty:
            facultad_full_df = facultad_full_df.sort_values("Cantidad", ascending=False)
            facultad_full_df["Etiqueta visual"] = facultad_full_df["Facultad"].apply(short_faculty_label)
            facultad_full_df["Porcentaje"] = facultad_full_df["Porcentaje"].map(lambda x: f"{float(x):.1f}%")

            with st.expander("Ver distribución completa por unidad académica"):
                st.dataframe(
                    facultad_full_df[
                        ["Facultad", "Etiqueta visual", "Cantidad", "Porcentaje"]
                    ],
                    use_container_width=True,
                    hide_index=True,
                    height=420,
                )
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    

    st.markdown(
        """
        <div class="method-note">
            <strong>Nota metodológica:</strong> esta sección describe la composición de la muestra encuestada.
            La distribución por unidad académica evidencia una mayor concentración en determinadas facultades;
            por ello, los resultados no deben interpretarse como representación proporcional de toda la UCE.
        </div>
        """,
        unsafe_allow_html=True,
    )
