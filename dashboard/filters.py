# dashboard/filters.py
import pandas as pd
import streamlit as st

from dashboard.common import find_first_existing_column


def _unique_options(df: pd.DataFrame, col: str) -> list[str]:
    if df is None or df.empty or not col or col not in df.columns:
        return []

    return sorted(
        df[col]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", "No especificado")
        .unique()
        .tolist()
    )

def _apply_multiselect_filter(
    df: pd.DataFrame,
    col: str | None,
    label: str,
    active_filters: dict,
    key: str,
) -> pd.DataFrame:
    if df is None or df.empty or not col or col not in df.columns:
        return df

    options = _unique_options(df, col)

    if not options:
        return df

    selected = st.multiselect(
        label,
        options,
        default=[],
        key=f"filter_{key}",
        placeholder="Todos",
        help="Deja vacío para incluir todas las categorías.",
    )

    active_filters[key] = selected if selected else "Todos"

    if not selected:
        return df

    return df[df[col].astype(str).str.strip().isin(selected)].copy()

def render_global_filters(df: pd.DataFrame):
    if df is None or df.empty:
        return df, {}

    filtered = df.copy()
    active_filters = {}

    edad_col = find_first_existing_column(
        df,
        ["edad", "rango de edad", "¿Cuál es tu edad?"],
    )

    genero_col = find_first_existing_column(
        df,
        ["genero", "género", "sexo", "gender"],
    )

    rol_col = find_first_existing_column(
        df,
        ["rol", "rol dentro de la universidad", "rol_uce"],
    )

    facultad_col = find_first_existing_column(
        df,
        ["facultad", "unidad académica", "unidad academica"],
    )

    quito_col = find_first_existing_column(
        df,
        ["quito", "reside en quito", "residencia"],
    )

    confianza_col = find_first_existing_column(
        df,
        ["confianza_idx_round", "confianza_idx"],
    )

    with st.sidebar.expander("Filtros de análisis", expanded=False):
        filtered = _apply_multiselect_filter(
            filtered,
            edad_col,
            "Rango de edad",
            active_filters,
            "edad",
        )

        filtered = _apply_multiselect_filter(
            filtered,
            genero_col,
            "Género",
            active_filters,
            "genero",
        )

        filtered = _apply_multiselect_filter(
            filtered,
            rol_col,
            "Rol institucional",
            active_filters,
            "rol",
        )

        filtered = _apply_multiselect_filter(
            filtered,
            facultad_col,
            "Facultad",
            active_filters,
            "facultad",
        )

        filtered = _apply_multiselect_filter(
            filtered,
            quito_col,
            "Residencia",
            active_filters,
            "residencia",
        )

        if not filtered.empty and confianza_col and confianza_col in filtered.columns:
            confianza_num = pd.to_numeric(filtered[confianza_col], errors="coerce")

            if confianza_num.notna().any():
                min_v = int(confianza_num.min())
                max_v = int(confianza_num.max())

                selected_range = st.slider(
                    "Confianza electoral",
                    min_value=min_v,
                    max_value=max_v,
                    value=(min_v, max_v),
                    key="filter_confianza",
                )

                mask = confianza_num.between(selected_range[0], selected_range[1])
                filtered = filtered.loc[mask].copy()
                active_filters["confianza"] = selected_range

        st.caption(f"Muestra filtrada: {len(filtered):,} registros")

    return filtered, active_filters