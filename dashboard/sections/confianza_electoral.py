import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from dashboard.components import topbar, kpi_card
from dashboard.common import (
    PLOTLY_CONFIG,
    LIKERT_LABELS,
    LIKERT_ORDER,
    LIKERT_COLORS,
    find_first_existing_column,
    empty_state,
    likert_to_numeric,
    make_likert_distribution,
    positive_count,
    render_card_header,
    render_note,
    safe_text,
)


AGE_ORDER = ["18-24", "25-34", "35-44", "45-54", "55-64"]


# =========================================================
# Utilidades de preparación
# =========================================================

def _pct(count: int, total: int) -> float:
    return round(count / total * 100, 1) if total else 0.0


def _clean_text_series(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def _normalize_age(value) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip()
    text = text.replace("–", "-").replace("—", "-")

    replacements = {
        "18 a 24": "18-24",
        "25 a 34": "25-34",
        "35 a 44": "35-44",
        "45 a 54": "45-54",
        "55 a 64": "55-64",
    }

    for old, new in replacements.items():
        if old in text:
            return new

    for group in AGE_ORDER:
        if group in text:
            return group

    return text if text in AGE_ORDER else None


def _age_numeric(series: pd.Series) -> pd.Series:
    mapping = {
        "18-24": 21,
        "25-34": 29.5,
        "35-44": 39.5,
        "45-54": 49.5,
        "55-64": 59.5,
    }
    return series.map(mapping)


def _ordered_age_series(df: pd.DataFrame, edad_col: str | None) -> pd.Series:
    if not edad_col or edad_col not in df.columns:
        return pd.Series([None] * len(df), index=df.index)

    return _clean_text_series(df[edad_col]).map(_normalize_age)


def _map_by_dictionary(series: pd.Series, mapping: dict[str, int | float]) -> pd.Series:
    cleaned = _clean_text_series(series)
    direct = cleaned.map(mapping)

    if direct.notna().sum() > 0:
        return direct

    lowered_map = {str(k).lower().strip(): v for k, v in mapping.items()}
    return cleaned.str.lower().str.strip().map(lowered_map)


def _prepare_columns(df: pd.DataFrame) -> dict[str, str | None]:
    return {
        "edad": find_first_existing_column(df, ["edad", "rango de edad", "¿Cuál es tu edad?"]),
        "genero": find_first_existing_column(df, ["genero", "género", "sexo"]),
        "rol": find_first_existing_column(df, ["rol_uce", "rol", "rol dentro de la universidad"]),
        "facultad": find_first_existing_column(df, ["facultad", "unidad académica", "unidad academica"]),
        "limpieza": find_first_existing_column(
            df,
            [
                "confianza_limpieza",
                "limpieza",
                "transparencia del proceso electoral",
                "confianza en la limpieza",
            ],
        ),
        "fraude": find_first_existing_column(
            df,
            [
                "confianza_fraude",
                "fraude",
                "manipulación electoral",
                "alteración del proceso electoral",
            ],
        ),
        "indice": find_first_existing_column(df, ["confianza_idx", "confianza_idx_round"]),
        "indice_round": find_first_existing_column(df, ["confianza_idx_round", "confianza_idx"]),
        "influencia_voto": find_first_existing_column(
            df,
            [
                "¿Considera que el uso de IA en campañas digitales influyó en su decisión de voto en las elecciones presidenciales de 2025?",
                "influyó en su decisión de voto",
                "decision de voto",
                "decisión de voto",
            ],
        ),
        "cambio_confianza": find_first_existing_column(
            df,
            [
                "¿Ha cambiado su confianza en el proceso electoral al saber que existen bots, deepfakes o manipulación mediante IA?",
                "ha cambiado su confianza",
                "ahora confío menos",
                "bots, deepfakes o manipulación mediante IA",
            ],
        ),
        "exposicion": find_first_existing_column(
            df,
            [
                "exposicion_idx",
                "indice_exposicion_digital",
                "exposure_index",
                "Durante la campaña presidencial entre Luisa González y Daniel Noboa, ¿con qué frecuencia vio o recibió contenido político en redes sociales o plataformas digitales?",
                "frecuencia vio o recibió contenido político",
                "contenido político en redes sociales",
            ],
        ),
        "automatizacion": find_first_existing_column(
            df,
            [
                "percibe_automatizacion",
                "automatizacion",
                "automatización",
                "herramientas automatizadas",
            ],
        ),
        "falso": find_first_existing_column(
            df,
            [
                "¿Vio alguna vez un video, imagen, audio o noticia política",
                "video, imagen, audio o noticia política",
                "contenido falso",
                "contenido manipulado",
                "generado con IA",
                "falso",
            ],
        ),
        "bots_reduce_confianza": find_first_existing_column(
            df,
            [
                "La presencia de bots o cuentas falsas en redes sociales reduce mi confianza",
                "bots o cuentas falsas",
                "reduce mi confianza en la información política digital",
            ],
        ),
        "deepfake_desconfianza": find_first_existing_column(
            df,
            [
                "La existencia de deepfakes o contenido manipulado me hace desconfiar",
                "deepfakes o contenido manipulado",
                "desconfiar más de las campañas políticas digitales",
            ],
        ),
        "manipulacion_personalizada": find_first_existing_column(
            df,
            [
                "Los partidos pueden manipular mi opinión mediante mensajes personalizados creados con IA",
                "mensajes personalizados creados con IA",
                "manipular mi opinión",
            ],
        ),
        "transparencia_ia": find_first_existing_column(
            df,
            [
                "La inteligencia artificial puede mejorar la transparencia del proceso electoral",
                "mejorar la transparencia del proceso electoral",
            ],
        ),
        "verificacion": find_first_existing_column(
            df,
            [
                "Realiza alguna verificación",
                "chequea fuentes",
                "información política digital antes de compartirla",
            ],
        ),
        "participacion": find_first_existing_column(
            df,
            [
                "Participó activamente en redes sociales",
                "participó activamente",
                "medios digitales durantes las ultimas elecciones",
            ],
        ),
    }


def build_confidence_index(df: pd.DataFrame, cols: dict[str, str | None]) -> pd.Series:
    """
    Índice 1-5 de confianza electoral.
    Si existe confianza_idx, se usa directamente. Si no, se calcula como:
    promedio(confianza_limpieza, reverso de percepción de fraude).
    """
    indice_col = cols.get("indice")
    if indice_col and indice_col in df.columns:
        numeric = pd.to_numeric(df[indice_col], errors="coerce")
        if numeric.notna().sum() > 0:
            return numeric.clip(1, 5)

    limpieza_col = cols.get("limpieza")
    fraude_col = cols.get("fraude")
    components = []

    if limpieza_col and limpieza_col in df.columns:
        components.append(likert_to_numeric(df[limpieza_col]))

    if fraude_col and fraude_col in df.columns:
        fraude_num = likert_to_numeric(df[fraude_col])
        components.append(6 - fraude_num)

    if not components:
        return pd.Series([np.nan] * len(df), index=df.index)

    return pd.concat(components, axis=1).mean(axis=1).clip(1, 5)


def build_exposure_score(df: pd.DataFrame, cols: dict[str, str | None] | None = None) -> pd.Series:
    """
    Índice exploratorio 1-5 de exposición digital a IA/contenido político.
    Combina frecuencia de contenido político, percepción de automatización y exposición a contenido falso/manipulado.
    """
    if cols is None:
        cols = _prepare_columns(df)

    components = []

    exposicion_col = cols.get("exposicion")
    if exposicion_col and exposicion_col in df.columns:
        numeric = pd.to_numeric(df[exposicion_col], errors="coerce")
        if numeric.notna().sum() > 0:
            components.append(numeric.clip(1, 5))
        else:
            components.append(
                _map_by_dictionary(
                    df[exposicion_col],
                    {
                        "Nunca": 1,
                        "Rara vez": 2,
                        "Varias veces a la semana": 3,
                        "Una vez al día": 4,
                        "Varias veces al día": 5,
                    },
                )
            )

    automatizacion_col = cols.get("automatizacion")
    if automatizacion_col and automatizacion_col in df.columns:
        components.append(
            _map_by_dictionary(
                df[automatizacion_col],
                {
                    "No": 1,
                    "Tal vez, pero no estoy seguro/a": 3,
                    "Sí, lo he notado claramente": 5,
                },
            )
        )

    falso_col = cols.get("falso")
    if falso_col and falso_col in df.columns:
        components.append(
            _map_by_dictionary(
                df[falso_col],
                {
                    "No": 1,
                    "No estoy seguro/a": 3,
                    "Sí, algunas veces": 4,
                    "Sí, muchas veces": 5,
                },
            )
        )

    if not components:
        return pd.Series([np.nan] * len(df), index=df.index)

    return pd.concat(components, axis=1).mean(axis=1).clip(1, 5)


def build_ai_risk_score(df: pd.DataFrame, cols: dict[str, str | None] | None = None) -> pd.Series:
    """
    Índice 1-5 de exposición/riesgo percibido por IA para contrastar H1 y H2.
    Operacionaliza bots, deepfakes y microsegmentación política mediante tres ítems Likert:
    manipulación personalizada, bots/cuentas falsas y deepfakes/contenido manipulado.
    """
    if cols is None:
        cols = _prepare_columns(df)

    components = []
    for key in ["manipulacion_personalizada", "bots_reduce_confianza", "deepfake_desconfianza"]:
        col = cols.get(key)
        if col and col in df.columns:
            values = likert_to_numeric(df[col])
            if values.notna().sum() > 0:
                components.append(values)

    if not components:
        return build_exposure_score(df, cols)

    return pd.concat(components, axis=1).mean(axis=1).clip(1, 5)


def build_media_literacy_score(df: pd.DataFrame, cols: dict[str, str | None] | None = None) -> pd.Series:
    """
    Proxy 1-5 de alfabetización mediática usando verificación informativa antes de compartir.
    Se interpreta como capacidad/práctica de contraste de fuentes, no como medición integral de alfabetización.
    """
    if cols is None:
        cols = _prepare_columns(df)

    col = cols.get("verificacion")
    if not col or col not in df.columns:
        return pd.Series([np.nan] * len(df), index=df.index)

    return _map_by_dictionary(
        df[col],
        {
            "Nunca": 1,
            "Rara vez": 2,
            "A veces": 3,
            "Siempre": 5,
        },
    )


def _verification_group_series(df: pd.DataFrame, cols: dict[str, str | None]) -> pd.Series:
    col = cols.get("verificacion")
    if not col or col not in df.columns:
        return pd.Series([None] * len(df), index=df.index)

    values = _clean_text_series(df[col])
    return values.map(
        {
            "Nunca": "Baja verificación",
            "Rara vez": "Baja verificación",
            "A veces": "Verificación media",
            "Siempre": "Alta verificación",
        }
    )


def _risk_level_series(series: pd.Series) -> pd.Series:
    return pd.cut(
        pd.to_numeric(series, errors="coerce"),
        bins=[0, 2.5, 3.5, 5.01],
        labels=["Bajo", "Medio", "Alto"],
        include_lowest=True,
        right=False,
    )


VERIFICATION_ORDER = ["Baja verificación", "Verificación media", "Alta verificación"]
RISK_LEVEL_ORDER = ["Bajo", "Medio", "Alto"]


def _analysis_frame(df: pd.DataFrame, cols: dict[str, str | None]) -> pd.DataFrame:
    out = df.copy()
    out["Rango de edad"] = _ordered_age_series(out, cols.get("edad"))
    out["Edad_num"] = _age_numeric(out["Rango de edad"])
    out["Exposición digital"] = build_exposure_score(out, cols)
    out["Riesgo IA"] = build_ai_risk_score(out, cols)
    out["Alfabetización mediática"] = build_media_literacy_score(out, cols)
    out["Nivel de verificación"] = _verification_group_series(out, cols)
    out["Confianza electoral"] = build_confidence_index(out, cols)
    out["Exposición Likert"] = out["Exposición digital"].round().clip(1, 5)
    out["Riesgo IA Likert"] = out["Riesgo IA"].round().clip(1, 5)
    out["Confianza Likert"] = out["Confianza electoral"].round().clip(1, 5)
    out["Nivel de riesgo IA"] = _risk_level_series(out["Riesgo IA"])
    return out


# =========================================================
# Gráficos base
# =========================================================

def make_stacked_bar(values: pd.DataFrame, title_y: str, height: int = 165):
    if values.empty or values["Cantidad"].sum() <= 0:
        return None

    fig = px.bar(
        values,
        x="Porcentaje",
        y=[title_y] * len(values),
        color="Respuesta",
        orientation="h",
        text="Porcentaje",
        category_orders={"Respuesta": LIKERT_ORDER},
        color_discrete_map=LIKERT_COLORS,
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        insidetextanchor="middle",
        cliponaxis=False,
        hovertemplate="<b>%{customdata}</b><br>Porcentaje: %{x:.1f}%<extra></extra>",
        customdata=values["Respuesta"],
    )

    fig.update_layout(
        barmode="stack",
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        xaxis=dict(visible=False, range=[0, 100]),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=4, b=50),
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.10,
            xanchor="left",
            x=0,
            font=dict(size=10),
        ),
        font=dict(size=11),
    )

    return fig


def make_category_bar(
    df: pd.DataFrame,
    col: str,
    order: list[str],
    height: int = 235,
    color_map: dict[str, str] | None = None,
):
    if df.empty or not col or col not in df.columns:
        return None

    counts = (
        _clean_text_series(df[col])
        .replace("", "No registrado")
        .value_counts()
    )

    ordered = [item for item in order if item in counts.index]
    remaining = [item for item in counts.index if item not in ordered]
    counts = counts.reindex(ordered + remaining).fillna(0).astype(int)
    counts = counts[counts > 0]

    total = counts.sum()
    if total == 0:
        return None

    chart_df = pd.DataFrame(
        {
            "Categoría": counts.index,
            "Cantidad": counts.values,
            "Porcentaje": (counts.values / total * 100).round(1),
        }
    )

    fig = px.bar(
        chart_df,
        x="Cantidad",
        y="Categoría",
        orientation="h",
        text="Porcentaje",
        color="Categoría",
        color_discrete_map=color_map or {},
        color_discrete_sequence=["#2563eb", "#93c5fd", "#f59e0b", "#ef4444", "#94a3b8"],
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False,
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
        margin=dict(l=0, r=58, t=4, b=16),
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#e5e7eb",
            zeroline=False,
            range=[0, max(total * 1.05, chart_df["Cantidad"].max() * 1.18)],
        ),
        yaxis=dict(title="", automargin=True),
        showlegend=False,
        font=dict(size=11),
    )

    return fig


def make_likert_matrix(items: list[dict], height: int = 310):
    rows = []

    for item in items:
        dist = item["dist"]
        if dist.empty:
            continue

        for _, row in dist.iterrows():
            rows.append(
                {
                    "Indicador": item["short"],
                    "Respuesta": row["Respuesta"],
                    "Porcentaje": row["Porcentaje"],
                    "Cantidad": row["Cantidad"],
                }
            )

    matrix_df = pd.DataFrame(rows)
    if matrix_df.empty:
        return None

    fig = px.bar(
        matrix_df,
        x="Porcentaje",
        y="Indicador",
        color="Respuesta",
        orientation="h",
        text="Porcentaje",
        category_orders={"Respuesta": LIKERT_ORDER},
        color_discrete_map=LIKERT_COLORS,
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        insidetextanchor="middle",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Respuesta: %{customdata[0]}<br>"
            "Cantidad: %{customdata[1]}<br>"
            "Porcentaje: %{x:.1f}%<extra></extra>"
        ),
        customdata=matrix_df[["Respuesta", "Cantidad"]],
    )

    fig.update_layout(
        barmode="stack",
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=0, r=10, t=8, b=70),
        xaxis=dict(visible=False, range=[0, 100]),
        yaxis=dict(title="", automargin=True, tickfont=dict(size=11)),
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.14,
            xanchor="left",
            x=0,
            font=dict(size=10),
        ),
    )

    return fig


def make_heatmap_exposure_confidence(analysis_df: pd.DataFrame, height: int = 390):
    plot_df = analysis_df.dropna(subset=["Exposición Likert", "Confianza Likert"]).copy()
    if plot_df.empty:
        return None

    plot_df["Exposición Likert"] = plot_df["Exposición Likert"].astype(int)
    plot_df["Confianza Likert"] = plot_df["Confianza Likert"].astype(int)

    count_matrix = pd.crosstab(plot_df["Confianza Likert"], plot_df["Exposición Likert"])
    count_matrix = count_matrix.reindex(index=[5, 4, 3, 2, 1], columns=[1, 2, 3, 4, 5], fill_value=0)

    total = int(count_matrix.values.sum())
    pct_matrix = (count_matrix / total * 100).round(1) if total else count_matrix.astype(float)

    text_matrix = count_matrix.astype(str)
    for y in count_matrix.index:
        for x in count_matrix.columns:
            count = int(count_matrix.loc[y, x])
            pct = float(pct_matrix.loc[y, x])
            text_matrix.loc[y, x] = "" if count == 0 else f"{count}<br><span style='font-size:10px'>{pct:.1f}%</span>"

    fig = go.Figure(
        data=go.Heatmap(
            z=pct_matrix.values,
            x=[str(x) for x in count_matrix.columns],
            y=[f"Confianza {y}" for y in count_matrix.index],
            colorscale=[
                [0.0, "#f8fafc"],
                [0.25, "#dbeafe"],
                [0.5, "#93c5fd"],
                [0.75, "#3b82f6"],
                [1.0, "#1d4ed8"],
            ],
            colorbar=dict(title="%", thickness=11, len=0.78),
            hovertemplate=(
                "Exposición: %{x}<br>"
                "%{y}<br>"
                "Densidad: %{z:.1f}%<extra></extra>"
            ),
        )
    )

    for row_idx, y in enumerate(count_matrix.index):
        for col_idx, x in enumerate(count_matrix.columns):
            label = text_matrix.loc[y, x]
            if label:
                fig.add_annotation(
                    x=str(x),
                    y=f"Confianza {y}",
                    text=label,
                    showarrow=False,
                    font=dict(size=11, color="#0f172a"),
                )

    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=8, r=8, t=28, b=42),
        xaxis=dict(
            title="Exposición digital percibida (1=baja, 5=alta)",
            side="top",
            tickfont=dict(size=11),
        ),
        yaxis=dict(title="", tickfont=dict(size=11)),
        font=dict(size=11),
    )

    return fig


def make_bubble_exposure_confidence(analysis_df: pd.DataFrame, height: int = 390):
    plot_df = analysis_df.dropna(subset=["Exposición Likert", "Confianza Likert"]).copy()
    if plot_df.empty:
        return None

    plot_df["Exposición Likert"] = plot_df["Exposición Likert"].astype(int)
    plot_df["Confianza Likert"] = plot_df["Confianza Likert"].astype(int)

    grouped = (
        plot_df
        .groupby(["Exposición Likert", "Confianza Likert"], observed=True)
        .size()
        .reset_index(name="Cantidad")
    )
    grouped["Porcentaje"] = (grouped["Cantidad"] / grouped["Cantidad"].sum() * 100).round(1)

    fig = px.scatter(
        grouped,
        x="Exposición Likert",
        y="Confianza Likert",
        size="Cantidad",
        color="Cantidad",
        color_continuous_scale="Blues",
        text="Cantidad",
        size_max=48,
        hover_data={"Porcentaje": ":.1f", "Cantidad": True},
    )

    fig.update_traces(
        marker=dict(line=dict(width=1.2, color="#ffffff"), opacity=0.82),
        textposition="middle center",
        textfont=dict(size=10, color="#0f172a"),
    )

    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=8, r=8, t=10, b=45),
        xaxis=dict(
            title="Exposición digital percibida (1-5)",
            range=[0.5, 5.5],
            dtick=1,
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        yaxis=dict(
            title="Confianza electoral (1-5)",
            range=[0.5, 5.5],
            dtick=1,
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        coloraxis_showscale=False,
        font=dict(size=11),
    )

    return fig


def make_scatter_exposure_confidence(
    analysis_df: pd.DataFrame,
    cols: dict[str, str | None],
    height: int = 390,
):
    plot_df = analysis_df.dropna(subset=["Exposición digital", "Confianza electoral"]).copy()
    if plot_df.empty:
        return None

    rng = np.random.default_rng(42)
    plot_df["Exposición visual"] = plot_df["Exposición digital"] + rng.normal(0, 0.045, len(plot_df))
    plot_df["Confianza visual"] = plot_df["Confianza electoral"] + rng.normal(0, 0.045, len(plot_df))

    hover_cols = ["Rango de edad"]
    for col in [cols.get("genero"), cols.get("rol"), cols.get("facultad")]:
        if col and col in plot_df.columns:
            hover_cols.append(col)

    fig = px.scatter(
        plot_df,
        x="Exposición visual",
        y="Confianza visual",
        color="Rango de edad" if "Rango de edad" in plot_df.columns else None,
        category_orders={"Rango de edad": AGE_ORDER},
        hover_data=hover_cols,
        opacity=0.72,
    )

    fig.update_traces(
        marker=dict(size=8.5, line=dict(width=0.5, color="#ffffff"))
    )

    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=8, r=8, t=10, b=45),
        xaxis=dict(
            title="Exposición percibida a IA, automatización o contenido manipulado",
            range=[0.7, 5.3],
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        yaxis=dict(
            title="Índice de confianza electoral",
            range=[0.7, 5.3],
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        legend_title_text="Rango de edad",
        font=dict(size=11),
    )

    return fig


def make_age_boxplot(analysis_df: pd.DataFrame, height: int = 390):
    plot_df = analysis_df.dropna(subset=["Rango de edad", "Confianza electoral"]).copy()
    plot_df = plot_df[plot_df["Rango de edad"].isin(AGE_ORDER)]
    if plot_df.empty:
        return None

    fig = px.box(
        plot_df,
        x="Rango de edad",
        y="Confianza electoral",
        category_orders={"Rango de edad": AGE_ORDER},
        points=False,
    )

    medians = (
        plot_df.groupby("Rango de edad", observed=True)["Confianza electoral"]
        .median()
        .reindex(AGE_ORDER)
        .dropna()
        .reset_index()
    )

    fig.add_trace(
        go.Scatter(
            x=medians["Rango de edad"],
            y=medians["Confianza electoral"],
            mode="lines+markers",
            name="Mediana",
            line=dict(width=2, color="#10b981"),
            marker=dict(size=8, color="#10b981", line=dict(width=1, color="#ffffff")),
        )
    )

    fig.update_traces(
        selector=dict(type="box"),
        marker_color="#3b82f6",
        line_color="#2563eb",
        fillcolor="rgba(59,130,246,0.16)",
        hovertemplate="Rango: %{x}<br>Confianza: %{y:.2f}<extra></extra>",
    )

    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=8, r=8, t=12, b=45),
        xaxis=dict(title="", gridcolor="#e5e7eb"),
        yaxis=dict(
            title="Confianza electoral (1-5)",
            range=[0.7, 5.3],
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        legend=dict(orientation="h", yanchor="top", y=-0.14, xanchor="left", x=0),
        font=dict(size=11),
    )

    return fig


def _age_summary_html(analysis_df: pd.DataFrame) -> str:
    plot_df = analysis_df.dropna(subset=["Rango de edad", "Confianza electoral"]).copy()
    plot_df = plot_df[plot_df["Rango de edad"].isin(AGE_ORDER)]

    if plot_df.empty:
        return ""

    rows = []
    for age in AGE_ORDER:
        sub = plot_df[plot_df["Rango de edad"] == age]
        if sub.empty:
            continue

        median = sub["Confianza electoral"].median()
        q1 = sub["Confianza electoral"].quantile(0.25)
        q3 = sub["Confianza electoral"].quantile(0.75)
        n = len(sub)

        # IMPORTANTE:
        # No usar HTML multilínea indentado aquí. Streamlit/Markdown puede
        # interpretar las líneas con 4+ espacios como bloque de código y mostrar
        # los <div> en pantalla. Por eso se arma el HTML en una sola línea.
        rows.append(
            "<div class='ce-age-card'>"
            f"<div class='ce-age-title'>{safe_text(age)} años</div>"
            f"<div class='ce-age-value'>{median:.1f}</div>"
            f"<div class='ce-age-text'>mediana · n={n}</div>"
            f"<div class='ce-age-text'>IQR [{q1:.1f} – {q3:.1f}]</div>"
            "</div>"
        )

    return "<div class='ce-age-grid'>" + "".join(rows) + "</div>" if rows else ""

def make_spearman_chart(analysis_df: pd.DataFrame, cols: dict[str, str | None], height: int = 390):
    if analysis_df.empty or "Confianza electoral" not in analysis_df.columns:
        return None, pd.DataFrame()

    data = pd.DataFrame(index=analysis_df.index)
    data["Confianza electoral"] = analysis_df["Confianza electoral"]
    data["Exposición digital"] = analysis_df["Exposición digital"]
    if "Riesgo IA" in analysis_df.columns:
        data["Riesgo percibido por IA"] = analysis_df["Riesgo IA"]
    if "Alfabetización mediática" in analysis_df.columns:
        data["Alfabetización mediática"] = analysis_df["Alfabetización mediática"]
    data["Edad"] = analysis_df["Edad_num"]

    if cols.get("falso"):
        data["Contenido falso/manipulado"] = _map_by_dictionary(
            analysis_df[cols["falso"]],
            {
                "No": 1,
                "No estoy seguro/a": 3,
                "Sí, algunas veces": 4,
                "Sí, muchas veces": 5,
            },
        )

    if cols.get("automatizacion"):
        data["Percepción de automatización"] = _map_by_dictionary(
            analysis_df[cols["automatizacion"]],
            {
                "No": 1,
                "Tal vez, pero no estoy seguro/a": 3,
                "Sí, lo he notado claramente": 5,
            },
        )

    likert_candidates = {
        "Bots reducen confianza": cols.get("bots_reduce_confianza"),
        "Deepfakes generan desconfianza": cols.get("deepfake_desconfianza"),
        "Manipulación personalizada": cols.get("manipulacion_personalizada"),
        "IA mejora transparencia": cols.get("transparencia_ia"),
    }

    for label, col in likert_candidates.items():
        if col and col in analysis_df.columns:
            data[label] = likert_to_numeric(analysis_df[col])

    if cols.get("verificacion"):
        data["Verificación informativa"] = _map_by_dictionary(
            analysis_df[cols["verificacion"]],
            {"Nunca": 1, "Rara vez": 2, "A veces": 3, "Siempre": 5},
        )

    if cols.get("participacion"):
        data["Participación digital"] = _map_by_dictionary(
            analysis_df[cols["participacion"]],
            {"No": 1, "Prefiero no responder": 2, "Sí": 5},
        )

    rows = []
    target = data["Confianza electoral"]

    for col in data.columns:
        if col == "Confianza electoral":
            continue

        temp = pd.DataFrame({"x": data[col], "y": target}).dropna()
        if len(temp) < 10 or temp["x"].nunique() < 2 or temp["y"].nunique() < 2:
            continue

        rho = temp["x"].corr(temp["y"], method="spearman")
        p_value = np.nan
        try:
            from scipy.stats import spearmanr
            rho_s, p_value_s = spearmanr(temp["x"], temp["y"], nan_policy="omit")
            if not np.isnan(rho_s):
                rho = rho_s
            p_value = p_value_s
        except Exception:
            pass

        rows.append(
            {
                "Variable": col,
                "rho": round(float(rho), 3) if pd.notna(rho) else np.nan,
                "p_value": p_value,
                "n": len(temp),
            }
        )

    corr_df = pd.DataFrame(rows).dropna(subset=["rho"])
    if corr_df.empty:
        return None, corr_df

    corr_df["abs_rho"] = corr_df["rho"].abs()
    corr_df = corr_df.sort_values("abs_rho", ascending=True)
    corr_df["Sentido"] = np.where(corr_df["rho"] >= 0, "Asociación positiva", "Asociación negativa")
    corr_df["rho_label"] = corr_df["rho"].map(lambda x: f"{x:+.2f}")

    marker_colors = ["#10b981" if value >= 0 else "#ef4444" for value in corr_df["rho"]]

    fig = px.bar(
        corr_df,
        x="rho",
        y="Variable",
        orientation="h",
        text="rho_label",
        hover_data={"n": True, "p_value": ":.4f", "rho": ":.3f"},
    )
    fig.update_traces(
        marker_color=marker_colors,
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "rho: %{x:.3f}<br>"
            "n: %{customdata[0]}<br>"
            "p: %{customdata[1]:.4f}<extra></extra>"
        ),
        customdata=corr_df[["n", "p_value"]],
    )

    max_abs = max(corr_df["rho"].abs().max() * 1.25, 0.25)
    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=8, r=68, t=8, b=42),
        xaxis=dict(
            title="Coeficiente de Spearman (rho)",
            range=[-max_abs, max_abs],
            zeroline=True,
            zerolinecolor="#94a3b8",
            gridcolor="#e5e7eb",
        ),
        yaxis=dict(title="", automargin=True),
        showlegend=False,
        font=dict(size=11),
    )

    return fig, corr_df.sort_values("abs_rho", ascending=False)



def make_moderation_line_chart(analysis_df: pd.DataFrame, height: int = 410):
    plot_df = analysis_df.dropna(
        subset=["Riesgo IA", "Confianza electoral", "Nivel de verificación", "Nivel de riesgo IA"]
    ).copy()

    plot_df = plot_df[
        plot_df["Nivel de verificación"].isin(VERIFICATION_ORDER)
        & plot_df["Nivel de riesgo IA"].astype(str).isin(RISK_LEVEL_ORDER)
    ].copy()

    if plot_df.empty:
        return None, pd.DataFrame()

    grouped = (
        plot_df.groupby(["Nivel de verificación", "Nivel de riesgo IA"], observed=True)
        .agg(
            n=("Confianza electoral", "size"),
            confianza_media=("Confianza electoral", "mean"),
            confianza_mediana=("Confianza electoral", "median"),
        )
        .reset_index()
    )
    grouped["Nivel de verificación"] = pd.Categorical(
        grouped["Nivel de verificación"], categories=VERIFICATION_ORDER, ordered=True
    )
    grouped["Nivel de riesgo IA"] = pd.Categorical(
        grouped["Nivel de riesgo IA"].astype(str), categories=RISK_LEVEL_ORDER, ordered=True
    )
    grouped = grouped.sort_values(["Nivel de verificación", "Nivel de riesgo IA"])

    fig = px.line(
        grouped,
        x="Nivel de riesgo IA",
        y="confianza_media",
        color="Nivel de verificación",
        markers=True,
        category_orders={
            "Nivel de riesgo IA": RISK_LEVEL_ORDER,
            "Nivel de verificación": VERIFICATION_ORDER,
        },
        color_discrete_map={
            "Baja verificación": "#ef4444",
            "Verificación media": "#f59e0b",
            "Alta verificación": "#10b981",
        },
        hover_data={"n": True, "confianza_mediana": ":.2f", "confianza_media": ":.2f"},
    )

    fig.update_traces(
        mode="lines+markers",
        marker=dict(size=9, line=dict(width=1, color="#ffffff")),
        line=dict(width=2.5),
        hovertemplate=(
            "Verificación: %{fullData.name}<br>"
            "Riesgo IA: %{x}<br>"
            "Confianza media: %{y:.2f}<br>"
            "n: %{customdata[0]}<br>"
            "Mediana: %{customdata[1]:.2f}<extra></extra>"
        ),
    )

    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=8, r=8, t=12, b=54),
        xaxis=dict(title="Riesgo/exposición percibida por IA", gridcolor="#e5e7eb"),
        yaxis=dict(
            title="Confianza electoral promedio (1-5)",
            range=[1, 5],
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0),
        legend_title_text="Nivel de verificación",
        font=dict(size=11),
    )

    return fig, grouped

def compute_moderation_group_stats(analysis_df: pd.DataFrame) -> pd.DataFrame:
    base = analysis_df.dropna(subset=["Riesgo IA", "Confianza electoral", "Nivel de verificación"]).copy()
    base = base[base["Nivel de verificación"].isin(VERIFICATION_ORDER)].copy()

    rows = []
    for group in VERIFICATION_ORDER:
        temp = base[base["Nivel de verificación"] == group].copy()
        if len(temp) < 10 or temp["Riesgo IA"].nunique() < 2:
            continue

        rho = temp["Riesgo IA"].corr(temp["Confianza electoral"], method="spearman")
        p_value = np.nan
        slope = np.nan

        try:
            from scipy.stats import spearmanr, linregress
            rho_s, p_s = spearmanr(temp["Riesgo IA"], temp["Confianza electoral"], nan_policy="omit")
            if not np.isnan(rho_s):
                rho = rho_s
            p_value = p_s
            lr = linregress(temp["Riesgo IA"], temp["Confianza electoral"])
            slope = lr.slope
        except Exception:
            try:
                slope = np.polyfit(temp["Riesgo IA"], temp["Confianza electoral"], 1)[0]
            except Exception:
                slope = np.nan

        temp["Nivel de riesgo IA"] = _risk_level_series(temp["Riesgo IA"])
        means = temp.groupby("Nivel de riesgo IA", observed=True)["Confianza electoral"].mean()
        low_mean = means.get("Bajo", np.nan)
        high_mean = means.get("Alto", np.nan)
        delta_high_low = high_mean - low_mean if pd.notna(high_mean) and pd.notna(low_mean) else np.nan

        rows.append(
            {
                "Nivel de verificación": group,
                "n": int(len(temp)),
                "rho": round(float(rho), 3) if pd.notna(rho) else np.nan,
                "p_value": p_value,
                "pendiente": round(float(slope), 3) if pd.notna(slope) else np.nan,
                "media_riesgo_bajo": round(float(low_mean), 2) if pd.notna(low_mean) else np.nan,
                "media_riesgo_alto": round(float(high_mean), 2) if pd.notna(high_mean) else np.nan,
                "cambio_alto_vs_bajo": round(float(delta_high_low), 2) if pd.notna(delta_high_low) else np.nan,
            }
        )

    return pd.DataFrame(rows)


def compute_interaction_model(analysis_df: pd.DataFrame) -> dict:
    data = analysis_df.dropna(
        subset=["Riesgo IA", "Alfabetización mediática", "Confianza electoral"]
    ).copy()

    if len(data) < 30 or data["Riesgo IA"].nunique() < 2 or data["Alfabetización mediática"].nunique() < 2:
        return {}

    data["Xc"] = data["Riesgo IA"] - data["Riesgo IA"].mean()
    data["Mc"] = data["Alfabetización mediática"] - data["Alfabetización mediática"].mean()
    data["Interacción"] = data["Xc"] * data["Mc"]

    xmat = np.column_stack(
        [np.ones(len(data)), data["Xc"].to_numpy(), data["Mc"].to_numpy(), data["Interacción"].to_numpy()]
    )
    y = data["Confianza electoral"].to_numpy()

    try:
        beta = np.linalg.lstsq(xmat, y, rcond=None)[0]
        pred = xmat @ beta
        resid = y - pred
        n, k = xmat.shape
        s2 = float(resid @ resid) / max(n - k, 1)
        inv = np.linalg.inv(xmat.T @ xmat)
        se = np.sqrt(np.diag(s2 * inv))
        t_vals = beta / se
        p_vals = [np.nan] * len(beta)

        try:
            from scipy.stats import t as student_t
            p_vals = [2 * (1 - student_t.cdf(abs(t), df=n-k)) for t in t_vals]
        except Exception:
            pass

        ss_res = float(np.sum(resid ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot else np.nan

        return {
            "n": int(n),
            "beta_riesgo": float(beta[1]),
            "p_riesgo": float(p_vals[1]) if pd.notna(p_vals[1]) else np.nan,
            "beta_verificacion": float(beta[2]),
            "p_verificacion": float(p_vals[2]) if pd.notna(p_vals[2]) else np.nan,
            "beta_interaccion": float(beta[3]),
            "p_interaccion": float(p_vals[3]) if pd.notna(p_vals[3]) else np.nan,
            "r2": float(r2) if pd.notna(r2) else np.nan,
        }
    except Exception:
        return {}


def _format_p(value) -> str:
    if pd.isna(value):
        return "N/D"
    if value < 0.001:
        return "<0.001"
    return f"{value:.3f}"


def _h2_summary_html(group_stats: pd.DataFrame, model: dict) -> str:
    if group_stats.empty:
        return ""

    def get_slope(group: str):
        row = group_stats[group_stats["Nivel de verificación"] == group]
        if row.empty:
            return np.nan
        return row.iloc[0]["pendiente"]

    low_slope = get_slope("Baja verificación")
    high_slope = get_slope("Alta verificación")
    p_interaction = model.get("p_interaccion", np.nan) if model else np.nan

    has_protective_pattern = pd.notna(low_slope) and pd.notna(high_slope) and abs(high_slope) < abs(low_slope)
    reading_text = "Tendencia exploratoria compatible" if has_protective_pattern else "Evidencia no concluyente"

    if pd.isna(p_interaction):
        technical_text = "modelo exploratorio"
        technical_detail = "p de interacción no disponible"
    elif p_interaction < 0.05:
        technical_text = "interacción significativa"
        technical_detail = f"modelo lineal: p = {_format_p(p_interaction)}"
    else:
        technical_text = "interacción no significativa"
        technical_detail = f"modelo lineal: p = {_format_p(p_interaction)}"

    return (
        "<div class='ce-h2-grid'>"
        "<div class='ce-h2-card red'><div class='ce-h2-label'>Baja verificación</div>"
        f"<div class='ce-h2-value'>{low_slope:+.3f}</div>"
        "<div class='ce-h2-text'>pendiente riesgo IA → confianza; valores más negativos indican mayor caída.</div></div>"
        "<div class='ce-h2-card green'><div class='ce-h2-label'>Alta verificación</div>"
        f"<div class='ce-h2-value'>{high_slope:+.3f}</div>"
        "<div class='ce-h2-text'>si la pendiente es menos negativa, la verificación funciona como posible amortiguador.</div></div>"
        "<div class='ce-h2-card yellow'><div class='ce-h2-label'>Lectura de H2</div>"
        f"<div class='ce-h2-value small'>{safe_text(reading_text)}</div>"
        "<div class='ce-h2-text'>lectura descriptiva; no implica causalidad ni confirmación fuerte.</div></div>"
        "<div class='ce-h2-card blue'><div class='ce-h2-label'>Detalle técnico</div>"
        f"<div class='ce-h2-value small'>{safe_text(technical_text)}</div>"
        f"<div class='ce-h2-text'>{safe_text(technical_detail)} · usar como apoyo, no como mensaje central.</div></div>"
        "</div>"
    )

def make_moderation_heatmap(analysis_df: pd.DataFrame, height: int = 360):
    plot_df = analysis_df.dropna(subset=["Nivel de verificación", "Nivel de riesgo IA", "Confianza electoral"]).copy()
    plot_df = plot_df[
        plot_df["Nivel de verificación"].isin(VERIFICATION_ORDER)
        & plot_df["Nivel de riesgo IA"].astype(str).isin(RISK_LEVEL_ORDER)
    ].copy()

    if plot_df.empty:
        return None

    y_order = ["Alta verificación", "Verificación media", "Baja verificación"]    

    grouped = (
        plot_df.groupby(["Nivel de verificación", "Nivel de riesgo IA"], observed=True)
        .agg(
            confianza_media=("Confianza electoral", "mean"),
            n=("Confianza electoral", "size"),
        )
        .reset_index()
    )

    value_matrix = grouped.pivot(
        index="Nivel de verificación",
        columns="Nivel de riesgo IA",
        values="confianza_media",
    ).reindex(index=y_order, columns=RISK_LEVEL_ORDER)

    n_matrix = grouped.pivot(
        index="Nivel de verificación",
        columns="Nivel de riesgo IA",
        values="n",
    ).reindex(index=y_order, columns=RISK_LEVEL_ORDER)

    valid_values = value_matrix.to_numpy(dtype=float)
    valid_values = valid_values[~np.isnan(valid_values)]

    if len(valid_values) == 0:
        return None

    zmin = max(1, float(valid_values.min()) - 0.12)
    zmax = min(5, float(valid_values.max()) + 0.12)

    fig = go.Figure(
        data=go.Heatmap(
            z=value_matrix.values,
            x=RISK_LEVEL_ORDER,
            y=y_order,
            zmin=zmin,
            zmax=zmax,
            xgap=4,
            ygap=4,
            colorscale=[
                [0.00, "#fff7ed"],
                [0.35, "#dbeafe"],
                [0.70, "#bfdbfe"],
                [1.00, "#dcfce7"],
            ],
            showscale=False,
            hovertemplate=(
                "Verificación: %{y}<br>"
                "Riesgo IA: %{x}<br>"
                "Confianza media: %{z:.2f}<extra></extra>"
            ),
        )
    ) 

    for y in y_order:
        for x in RISK_LEVEL_ORDER:
            val = value_matrix.loc[y, x] if y in value_matrix.index and x in value_matrix.columns else np.nan
            n_val = n_matrix.loc[y, x] if y in n_matrix.index and x in n_matrix.columns else np.nan

            if pd.notna(val):
                fig.add_annotation(
                    x=x,
                    y=y,
                    text=f"<b>{val:.2f}</b><br><span style='font-size:10px'>n={int(n_val)}</span>",
                    showarrow=False,
                    font=dict(size=12, color="#0f172a"),
                    align="center",
                )       

    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=10, r=10, t=8, b=44),
        xaxis=dict(
            title=dict(
                text="Riesgo/exposición percibida por IA",
                font=dict(size=12, color="#64748b"),
            ),
            tickfont=dict(size=11, color="#64748b"),
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=11, color="#64748b"),
            showgrid=False,
            zeroline=False,
        ),
        font=dict(size=11),
    )


    return fig


# =========================================================
# Bloques visuales
# =========================================================

def _render_kpis(
    survey_df: pd.DataFrame,
    cols: dict[str, str | None],
    n_survey: int,
):
    limpieza_col = cols.get("limpieza")
    fraude_col = cols.get("fraude")
    influencia_voto_col = cols.get("influencia_voto")
    cambio_confianza_col = cols.get("cambio_confianza")

    confianza_limpieza = positive_count(survey_df, limpieza_col)
    percibe_fraude = positive_count(survey_df, fraude_col)

    influyo_voto = 0
    if influencia_voto_col:
        influyo_voto = int(
            _clean_text_series(survey_df[influencia_voto_col])
            .isin(["Sí, algo", "Sí, mucho"])
            .sum()
        )

    confia_menos = 0
    if cambio_confianza_col:
        confia_menos = int(
            _clean_text_series(survey_df[cambio_confianza_col])
            .eq("Sí, ahora confío menos")
            .sum()
        )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Confianza positiva",
            f"{_pct(confianza_limpieza, n_survey):.1f}%" if limpieza_col else "N/D",
            f"{confianza_limpieza:,} de {n_survey:,} · limpieza/transparencia",
            "blue",
        )

    with c2:
        kpi_card(
            "Riesgo percibido",
            f"{_pct(percibe_fraude, n_survey):.1f}%" if fraude_col else "N/D",
            f"{percibe_fraude:,} de {n_survey:,} · fraude o manipulación",
            "red",
        )

    with c3:
        kpi_card(
            "Influencia en voto",
            f"{_pct(influyo_voto, n_survey):.1f}%" if influencia_voto_col else "N/D",
            f"{influyo_voto:,} de {n_survey:,} · IA influyó algo o mucho",
            "yellow",
        )

    with c4:
        kpi_card(
            "Confianza reducida",
            f"{_pct(confia_menos, n_survey):.1f}%" if cambio_confianza_col else "N/D",
            f"{confia_menos:,} de {n_survey:,} · bots/deepfakes/IA",
            "red",
        )

    return {
        "confianza_limpieza": confianza_limpieza,
        "percibe_fraude": percibe_fraude,
        "influyo_voto": influyo_voto,
        "confia_menos": confia_menos,
    }


def _render_interpretation(metrics: dict[str, int], n_survey: int):
    st.markdown(
        f"""
        <div class="interpretation-grid">
            <div class="interpretation-box blue">
                <div class="interpretation-value">{_pct(metrics['confianza_limpieza'], n_survey):.1f}%</div>
                <div class="interpretation-label">
                    expresa una percepción favorable sobre la limpieza o transparencia del proceso electoral.
                </div>
            </div>
            <div class="interpretation-box red">
                <div class="interpretation-value">{_pct(metrics['percibe_fraude'], n_survey):.1f}%</div>
                <div class="interpretation-label">
                    percibe riesgo de fraude, manipulación o alteración del proceso electoral.
                </div>
            </div>
            <div class="interpretation-box yellow">
                <div class="interpretation-value">{_pct(metrics['influyo_voto'], n_survey):.1f}%</div>
                <div class="interpretation-label">
                    considera que la IA influyó algo o mucho en su decisión de voto.
                </div>
            </div>
            <div class="interpretation-box red">
                <div class="interpretation-value">{_pct(metrics['confia_menos'], n_survey):.1f}%</div>
                <div class="interpretation-label">
                    afirma que ahora confía menos al conocer la existencia de bots, deepfakes o manipulación mediante IA.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_summary_tab(survey_df: pd.DataFrame, cols: dict[str, str | None], metrics: dict[str, int], n_survey: int):
    limpieza_col = cols.get("limpieza")
    fraude_col = cols.get("fraude")
    influencia_voto_col = cols.get("influencia_voto")
    cambio_confianza_col = cols.get("cambio_confianza")


    with st.container(border=True, key="card_ce_matriz"):
        render_card_header(
            "Mapa de confianza electoral",
            "Distribución comparativa de los indicadores Likert: limpieza/transparencia electoral y riesgo de fraude o manipulación.",
        )

        confianza_items = [
            {"short": "Limpieza electoral", "dist": make_likert_distribution(survey_df, limpieza_col)},
            {"short": "Riesgo de fraude", "dist": make_likert_distribution(survey_df, fraude_col)},
        ]

        fig = make_likert_matrix(confianza_items, height=300)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            empty_state("No se encontraron columnas suficientes para construir la matriz de confianza electoral.")

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True, key="card_ce_limpieza"):
            render_card_header(
                "Confianza en la limpieza electoral",
                "Nivel de acuerdo con una percepción positiva sobre la limpieza o transparencia del proceso electoral.",
            )
            if limpieza_col:
                fig = make_stacked_bar(make_likert_distribution(survey_df, limpieza_col), "Limpieza electoral", height=155)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                st.markdown(
                    """
                    <div class="alert-info-blue">
                        Indicador positivo de confianza institucional: agrupa la percepción de limpieza y transparencia del proceso electoral.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna de confianza en limpieza electoral.")

    with col2:
        with st.container(border=True, key="card_ce_fraude"):
            render_card_header(
                "Percepción de fraude o manipulación",
                "Nivel de acuerdo con la posibilidad de fraude, manipulación o alteración del proceso electoral.",
            )
            if fraude_col:
                fig = make_stacked_bar(make_likert_distribution(survey_df, fraude_col), "Fraude/manipulación", height=155)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                st.markdown(
                    """
                    <div class="alert-danger">
                        Indicador crítico: expresa sospecha, incertidumbre o percepción de manipulación en el proceso electoral.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna de percepción de fraude o manipulación.")

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="large")

    with col3:
        with st.container(border=True, key="card_ce_influencia_voto"):
            render_card_header(
                "Influencia de IA en la decisión de voto",
                "Percepción ciudadana sobre si el uso de IA en campañas digitales influyó en su decisión electoral.",
            )
            if influencia_voto_col:
                fig = make_category_bar(
                    survey_df,
                    influencia_voto_col,
                    ["Nada", "Poco", "Sí, algo", "Sí, mucho", "No sé/no aplica"],
                    height=235,
                    color_map={
                        "Nada": "#94a3b8",
                        "Poco": "#93c5fd",
                        "Sí, algo": "#f59e0b",
                        "Sí, mucho": "#ef4444",
                        "No sé/no aplica": "#cbd5e1",
                    },
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                st.markdown(
                    """
                    <div class="alert-warning">
                        Conecta la exposición a campañas digitales con una incidencia subjetiva reportada por los encuestados.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna sobre influencia de IA en la decisión de voto.")

    with col4:
        with st.container(border=True, key="card_ce_cambio_confianza"):
            render_card_header(
                "Cambio de confianza por bots/deepfakes/IA",
                "Variación de la confianza al conocer la existencia de bots, deepfakes o manipulación mediante IA.",
            )
            if cambio_confianza_col:
                fig = make_category_bar(
                    survey_df,
                    cambio_confianza_col,
                    ["Sí, ahora confío menos", "No ha cambiado", "Sí, ahora confío más", "No sé"],
                    height=235,
                    color_map={
                        "Sí, ahora confío menos": "#ef4444",
                        "No ha cambiado": "#94a3b8",
                        "Sí, ahora confío más": "#10b981",
                        "No sé": "#cbd5e1",
                    },
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                st.markdown(
                    """
                    <div class="alert-danger">
                        Mide la erosión, estabilidad o refuerzo de la confianza electoral frente a prácticas digitales asociadas con IA.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                empty_state("No se encontró la columna sobre cambio de confianza electoral.")

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_ce_interpretacion"):
        render_card_header(
            "Síntesis interpretativa",
            "Lectura integrada de los indicadores de confianza electoral.",
        )

        st.markdown(
            f"""
            <div class="ce-summary-reading">
                <div class="ce-summary-reading-item blue">
                    <strong>Confianza institucional</strong>
                    <span>{_pct(metrics['confianza_limpieza'], n_survey):.1f}% expresa percepción favorable sobre limpieza o transparencia electoral.</span>
                </div>
                <div class="ce-summary-reading-item red">
                    <strong>Riesgo electoral percibido</strong>
                    <span>{_pct(metrics['percibe_fraude'], n_survey):.1f}% percibe riesgo de fraude, manipulación o alteración del proceso.</span>
                </div>
                <div class="ce-summary-reading-item yellow">
                    <strong>Incidencia subjetiva de IA</strong>
                    <span>{_pct(metrics['influyo_voto'], n_survey):.1f}% considera que la IA influyó algo o mucho en su decisión de voto.</span>
                </div>
                <div class="ce-summary-reading-item red">
                    <strong>Erosión de confianza</strong>
                    <span>{_pct(metrics['confia_menos'], n_survey):.1f}% afirma confiar menos al conocer bots, deepfakes o manipulación mediante IA.</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )            

    st.markdown(
        """
        <div class="method-note">
            <strong>Nota metodológica:</strong> en indicadores Likert, los porcentajes positivos agrupan
            "De acuerdo" y "Totalmente de acuerdo". Los resultados describen la muestra encuestada y no implican causalidad.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_exposure_tab(analysis_df: pd.DataFrame, cols: dict[str, str | None]):
    with st.container(border=True, key="card_ce_heatmap"):
        render_card_header(
            "Contraste H1: exposición digital vs confianza electoral",
            "Densidad de encuestados por combinación Likert. Valores más oscuros indican mayor concentración de respuestas.",
        )
        fig = make_heatmap_exposure_confidence(analysis_df, height=400)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
            render_note(
                "Lectura de H1: la exposición digital general se concentra en niveles medios y altos. El sustento negativo se observa con mayor claridad cuando la exposición se interpreta como riesgo percibido por IA —bots, deepfakes y manipulación personalizada—. Por ello, H1 se reporta como sustento parcial y descriptivo, no como causalidad.",
                "blue",
            )
        else:
            empty_state("No hay datos suficientes para construir el heatmap exposición-confianza.")

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_ce_dispersion"):
        render_card_header(
            "Relación entre exposición digital y confianza electoral",
            "Modo burbuja para frecuencia exacta y modo dispersión para observar casos individuales con jitter visual.",
        )

        mode = st.radio(
            "Tipo de visualización",
            ["Frecuencia (burbuja)", "Dispersión individual"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if mode == "Frecuencia (burbuja)":
            fig = make_bubble_exposure_confidence(analysis_df, height=395)
        else:
            fig = make_scatter_exposure_confidence(analysis_df, cols, height=395)

        if fig:
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
            render_note(
                "Las variables Likert generan pocas posiciones posibles; por eso la burbuja resume frecuencia y la dispersión usa jitter solo para separar puntos superpuestos.",
                "blue",
            )
        else:
            empty_state("No hay datos numéricos suficientes para graficar exposición y confianza.")

def _h2_detail_table_html(group_stats: pd.DataFrame) -> str:
    if group_stats.empty:
        return ""

    def fmt(value, decimals=3):
        if pd.isna(value):
            return "N/D"
        return f"{float(value):.{decimals}f}"

    rows = []

    for _, row in group_stats.iterrows():
        rows.append(
            "<tr>"
            f"<td class='left'>{safe_text(row['Nivel de verificación'])}</td>"
            f"<td>{int(row['n'])}</td>"
            f"<td>{fmt(row['rho'], 3)}</td>"
            f"<td>{_format_p(row['p_value'])}</td>"
            f"<td>{fmt(row['pendiente'], 3)}</td>"
            f"<td>{fmt(row['media_riesgo_bajo'], 2)}</td>"
            f"<td>{fmt(row['media_riesgo_alto'], 2)}</td>"
            f"<td>{fmt(row['cambio_alto_vs_bajo'], 2)}</td>"
            "</tr>"
        )

    return (
        "<div class='ce-h2-table-wrap'>"
        "<table class='ce-h2-table'>"
        "<thead><tr>"
        "<th>Verificación</th>"
        "<th>n</th>"
        "<th>rho</th>"
        "<th>p</th>"
        "<th>Pendiente</th>"
        "<th>Media riesgo bajo</th>"
        "<th>Media riesgo alto</th>"
        "<th>Δ alto-bajo</th>"
        "</tr></thead>"
        "<tbody>"
        + "".join(rows) +
        "</tbody></table></div>"
    )


def _render_h2_tab(analysis_df: pd.DataFrame):
    with st.container(border=True, key="card_ce_h2_definicion"):
        render_card_header(
            "H2: verificación informativa y confianza electoral",
            "Se analiza si la práctica de verificar información política digital reduce la pérdida de confianza frente al riesgo percibido por bots, deepfakes y microsegmentación política.",
        )
        st.markdown(
            "<div class='ce-hypothesis-box'>"
            "<strong>Operacionalización:</strong> X = riesgo/exposición percibida por IA; "
            "M = verificación informativa antes de compartir; Y = índice de confianza electoral. "
            "La evidencia esperada para H2 es que la caída de confianza sea menor entre quienes verifican con mayor frecuencia."
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.35, 1], gap="large")

    with col1:
        with st.container(border=True, key="card_ce_h2_lineas"):
            render_card_header(
                "Riesgo percibido por IA y confianza según verificación",
                "Gráfico de interacción: si la línea de alta verificación cae menos que la de baja verificación, se observa un posible efecto amortiguador.",
            )
            fig, grouped = make_moderation_line_chart(analysis_df, height=420)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                render_note(
                    "El eje X resume bots, deepfakes y mensajes personalizados con IA. El eje Y muestra la confianza electoral promedio. Los tamaños de grupo y valores exactos se reportan en la tabla técnica inferior.",
                    "blue",
                )
            else:
                empty_state("No hay datos suficientes para graficar la interacción H2.")

    with col2:
        with st.container(border=True, key="card_ce_h2_heatmap"):
            render_card_header(
                "Matriz de confianza promedio",
                "Cruce entre nivel de verificación y riesgo percibido por IA.",
            )
            fig = make_moderation_heatmap(analysis_df, height=365)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                render_note(
                    "Lectura: valores más altos indican mayor confianza promedio. Cada celda muestra el promedio de confianza y el tamaño del grupo.",
                    "blue",
                )         
            else:
                empty_state("No hay datos suficientes para construir la matriz H2.")

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    group_stats = compute_moderation_group_stats(analysis_df)
    model = compute_interaction_model(analysis_df)

    with st.container(border=True, key="card_ce_h2_resumen"):
        render_card_header(
            "Lectura interpretativa de H2",
            "Resumen de la tendencia observada por nivel de verificación. Los indicadores técnicos se usan como apoyo y no como afirmación causal.",
        )
        html = _h2_summary_html(group_stats, model)
        if html:
            st.markdown(html, unsafe_allow_html=True)
            if model and pd.notna(model.get("p_interaccion", np.nan)) and model.get("p_interaccion", np.nan) >= 0.05:
                render_note(
                    "Lectura: la dirección de las pendientes es compatible con H2 porque la caída de confianza es más débil en alta verificación. Sin embargo, la interacción estadística no alcanza significancia, por lo que se presenta como tendencia exploratoria compatible y no como confirmación fuerte.",
                    "yellow",
                )
            else:
                render_note(
                    "Lectura: el patrón sugiere que la verificación informativa puede amortiguar la relación entre riesgo percibido por IA y confianza electoral.",
                    "green",
                )
        else:
            empty_state("No hay datos suficientes para calcular el resumen de moderación.")

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)


    with st.expander("Ver detalle técnico de H2"):
        with st.container(border=True, key="card_ce_h2_tabla"):
            render_card_header(
                "Detalle técnico de H2",
                "Tabla de apoyo: Spearman y pendiente lineal dentro de cada grupo de verificación.",
            )

            if not group_stats.empty:
                st.markdown(_h2_detail_table_html(group_stats), unsafe_allow_html=True)
                render_note(
                    "Criterio de lectura: la pendiente es menos negativa en alta verificación (-0.079) que en baja verificación (-0.139), lo que sugiere un posible efecto amortiguador. Este resultado se reporta como evidencia exploratoria, no como confirmación causal.",
                    "green",
                )
            else:
                empty_state("No se pudieron calcular pendientes por grupo de verificación.")        

def _render_association_tab(analysis_df: pd.DataFrame, cols: dict[str, str | None]):
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True, key="card_ce_edad_boxplot"):
            render_card_header(
                "Confianza electoral por rango de edad",
                "Boxplot con mediana, IQR y rango completo. Se conserva el rango etario 18–64 años.",
            )
            fig = make_age_boxplot(analysis_df, height=390)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                html = _age_summary_html(analysis_df)
                if html:
                    st.markdown(html, unsafe_allow_html=True)
            else:
                empty_state("No hay datos de edad y confianza suficientes para construir el boxplot.")

    with col2:
        with st.container(border=True, key="card_ce_spearman"):
            render_card_header(
                "Correlaciones de Spearman con confianza electoral",
                "Asociaciones ordinales exploratorias. Spearman es apropiado para variables Likert y rangos categóricos.",
            )
            fig, corr_df = make_spearman_chart(analysis_df, cols, height=390)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                render_note(
                    "Interpretación: rho positivo indica asociación con mayor confianza; rho negativo indica asociación con menor confianza. No equivale a causalidad.",
                    "yellow",
                )
            else:
                empty_state("No se pudieron calcular correlaciones ordinales suficientes.")

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_ce_metodologia"):
        st.markdown(
            "<div class='ce-method-panel'>"
            "<div class='ce-method-title'>Lectura metodológica</div>"
            "<div class='ce-method-grid'>"
            "<div class='ce-method-item'><strong>1. Variable dependiente</strong><br>"
            "La confianza electoral se resume en un índice 1–5 que combina confianza en limpieza/transparencia y percepción inversa de fraude.</div>"
            "<div class='ce-method-item'><strong>2. Exposición Digital</strong><br>"
            "La exposición digital integra frecuencia de contenido político, percepción de automatización y exposición a contenido falso/manipulado.</div>"
            "<div class='ce-method-item'><strong>3. Edad</strong><br>"
            "El módulo conserva los rangos 18–24, 25–34, 35–44, 45–54 y 55–64 para mantener coherencia con la muestra final.</div>"
            "<div class='ce-method-item'><strong>4. Alcance</strong><br>"
            "Los gráficos muestran asociaciones descriptivas; no reemplazan inferencia causal ni generalizan fuera de la muestra UCE encuestada.</div>"
            "</div></div>",
            unsafe_allow_html=True,
        )


# =========================================================
# Render principal
# =========================================================

def render_confianza_electoral(survey_df: pd.DataFrame):
    n_survey = len(survey_df) if survey_df is not None and not survey_df.empty else 0

    topbar(
        title="Confianza electoral",
        subtitle=(
            "Análisis de la confianza ciudadana frente al proceso electoral y su posible afectación "
            "por exposición digital, bots, deepfakes, contenido manipulado e influencia de IA en la decisión de voto. "
            "Muestra con rango etario 18–64 años."
        ),
        pill_text=f"n = {n_survey:,} encuestas" if n_survey else "encuestas no cargadas",
    )

    if survey_df is None or survey_df.empty:
        empty_state("No se encontraron datos de encuesta para construir esta sección.")
        return

    cols = _prepare_columns(survey_df)
    analysis_df = _analysis_frame(survey_df, cols)

    metrics = _render_kpis(survey_df, cols, n_survey)

    st.markdown('<div class="ce-section-gap"></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Resumen de confianza",
            "H1: exposición y confianza",
            "H2: verificación informativa",
            "Validación complementaria",
        ]
    )

    with tab1:
        _render_summary_tab(survey_df, cols, metrics, n_survey)

    with tab2:
        _render_exposure_tab(analysis_df, cols)

    with tab3:
        _render_h2_tab(analysis_df)

    with tab4:
        _render_association_tab(analysis_df, cols)
