# dashboard/sections/modelos_predictivos.py

from __future__ import annotations

import html
import math
from typing import Iterable
from textwrap import dedent
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from dashboard.components import topbar, kpi_card
from dashboard.common import PLOTLY_CONFIG, empty_state, render_card_header, render_note
from dashboard.data_loader import (
    load_model_metrics_summary,
    load_model_metrics_by_seed_dashboard,
    load_confusion_matrix_3_levels,
    load_confusion_matrix_5_levels,
    load_feature_importance,
    load_model_interpretation_rules,
    load_simulator_feature_schema,
)

from dashboard.model_backend import predict_simulator


MODEL_COLORS = {
    "Random Forest": "#3b82f6",
    "Gradient Boosting": "#10b981",
    "Logistic Regression": "#f59e0b",
    "SVM": "#ef4444",
}

METRIC_LABELS = {
    "AUC_OvR": "AUC (OvR)",
    "Accuracy": "Exactitud",
    "F1_ponderado": "F1 ponderado",
    "QWK": "Kappa cuadrático (QWK)",
    "AUC OvR": "AUC (OvR)",
    "F1 ponderado": "F1 ponderado",
    "Kappa cuadrático (QWK)": "Kappa cuadrático (QWK)",
}

METRIC_DESCRIPTIONS = {
    "AUC_OvR": "Capacidad discriminativa del modelo con estrategia One-vs-Rest. Valores cercanos a 1 indican mejor separación entre clases.",
    "Accuracy": "Proporción de aciertos sobre el total. Es intuitiva, pero puede ser sensible al desbalance de clases.",
    "F1_ponderado": "Media armónica de precisión y sensibilidad, ponderada por el soporte de cada clase.",
    "QWK": "Acuerdo ponderado cuadráticamente. Penaliza más los errores lejanos entre niveles ordinales de confianza.",
}

METRIC_ORDER = ["AUC_OvR", "Accuracy", "F1_ponderado", "QWK"]
CONFIG_ORDER = ["3 niveles", "5 niveles"]
LEVELS_3 = ["Baja", "Media", "Alta"]
LEVELS_5 = ["Muy baja", "Baja", "Media", "Alta", "Muy alta"]

MAIN_CONFIG = "5 niveles"
SECONDARY_CONFIG = "3 niveles"



def _safe_count(df: pd.DataFrame | None) -> int:
    if df is None or df.empty:
        return 0
    return len(df)


def _fmt_float(value, digits: int = 3, default: str = "N/D") -> str:
    try:
        if value is None or pd.isna(value):
            return default
        return f"{float(value):.{digits}f}"
    except Exception:
        return str(value) if value not in [None, ""] else default


def _fmt_pct(value, digits: int = 1, default: str = "N/D") -> str:
    try:
        if value is None or pd.isna(value):
            return default
        value = float(value)
        if value <= 1.5:
            value *= 100
        return f"{value:.{digits}f}%"
    except Exception:
        return default


def _canonical_metric(col: str) -> str:
    c = str(col).strip()
    aliases = {
        "AUC OvR": "AUC_OvR",
        "AUC (OvR)": "AUC_OvR",
        "AUC": "AUC_OvR",
        "Exactitud": "Accuracy",
        "F1 ponderado": "F1_ponderado",
        "F1 Ponderado": "F1_ponderado",
        "Kappa cuadrático (QWK)": "QWK",
        "Kappa Cuadrático (QWK)": "QWK",
    }
    return aliases.get(c, c)


def _normalize_metrics_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    rename_map = {}
    for col in out.columns:
        clean = str(col).strip()
        if clean.lower() in {"model", "modelo"}:
            rename_map[col] = "Modelo"
        elif clean.lower() in {"config", "configuracion", "configuración"}:
            rename_map[col] = "Configuración"
        elif clean in ["AUC OvR", "AUC (OvR)", "AUC"]:
            rename_map[col] = "AUC_OvR"
        elif clean in ["F1 ponderado", "F1 Ponderado"]:
            rename_map[col] = "F1_ponderado"
        elif clean in ["Kappa cuadrático (QWK)", "Kappa Cuadrático (QWK)"]:
            rename_map[col] = "QWK"
        elif clean == "Exactitud":
            rename_map[col] = "Accuracy"
    out = out.rename(columns=rename_map)

    for metric in METRIC_ORDER:
        if metric in out.columns:
            out[metric] = pd.to_numeric(out[metric], errors="coerce")

    if "Configuración" in out.columns:
        out["Configuración"] = out["Configuración"].astype(str).str.replace("niveles", "niveles", regex=False)

    return out


def _available_metrics(df: pd.DataFrame) -> list[str]:
    return [m for m in METRIC_ORDER if m in df.columns and pd.to_numeric(df[m], errors="coerce").notna().any()]


def _default_metric(df: pd.DataFrame) -> str:
    metrics = _available_metrics(df)
    if "AUC_OvR" in metrics:
        return "AUC_OvR"
    return metrics[0] if metrics else "Accuracy"


def _config_options(df: pd.DataFrame) -> list[str]:
    if "Configuración" not in df.columns:
        return []
    existing = df["Configuración"].dropna().astype(str).unique().tolist()
    ordered = [c for c in CONFIG_ORDER if c in existing]
    ordered.extend([c for c in existing if c not in ordered])
    return ordered


def _model_options(df: pd.DataFrame) -> list[str]:
    if "Modelo" not in df.columns:
        return []
    existing = df["Modelo"].dropna().astype(str).unique().tolist()
    ordered = [m for m in MODEL_COLORS if m in existing]
    ordered.extend([m for m in existing if m not in ordered])
    return ordered


def _get_best_model(summary_df: pd.DataFrame, preferred_config: str = "3 niveles") -> pd.Series | None:
    if summary_df is None or summary_df.empty:
        return None
    df = _normalize_metrics_df(summary_df)
    metric = _default_metric(df)
    if metric not in df.columns:
        return df.iloc[0]
    temp = df.copy()
    if "Configuración" in temp.columns and preferred_config in temp["Configuración"].astype(str).unique():
        temp = temp[temp["Configuración"].astype(str) == preferred_config]
    temp[metric] = pd.to_numeric(temp[metric], errors="coerce")
    if temp[metric].notna().sum() == 0:
        return temp.iloc[0]
    return temp.sort_values(metric, ascending=False).iloc[0]


def _metric_description(metric: str) -> str:
    return METRIC_DESCRIPTIONS.get(_canonical_metric(metric), "Métrica de rendimiento del modelo.")


def _metric_label(metric: str) -> str:
    return METRIC_LABELS.get(_canonical_metric(metric), str(metric))


def _plotly_base_layout(fig: go.Figure, height: int, margin: dict | None = None) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=margin or dict(l=5, r=20, t=10, b=10),
        font=dict(size=11, color="#475569"),
    )
    return fig

def _esc(value) -> str:
    if value is None or pd.isna(value):
        return ""
    return html.escape(str(value))


def _render_html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)

def _compact_html(markup: str) -> str:
    return "\n".join(
        line.strip()
        for line in dedent(markup).splitlines()
        if line.strip()
    )   

def _single_select_control(
    label: str,
    options: list,
    default,
    key: str,
    format_func=lambda x: x,
    label_visibility: str = "visible",
):
    options = list(options)
    if not options:
        return None

    default_value = default if default in options else options[0]

    if hasattr(st, "segmented_control"):
        value = st.segmented_control(
            label,
            options,
            default=default_value,
            selection_mode="single",
            format_func=format_func,
            key=key,
            label_visibility=label_visibility,
        )
        return value or default_value

    if hasattr(st, "pills"):
        value = st.pills(
            label,
            options,
            default=default_value,
            selection_mode="single",
            format_func=format_func,
            key=key,
            label_visibility=label_visibility,
        )
        return value or default_value

    return st.radio(
        label,
        options,
        index=options.index(default_value),
        horizontal=True,
        format_func=format_func,
        key=key,
        label_visibility=label_visibility,
    )     
# -----------------------------------------------------------------------------
# Bloques visuales principales
# -----------------------------------------------------------------------------

def _render_method_warning(n_survey: int) -> None:
    render_note(
        (
            f"Nota metodológica: los modelos fueron entrenados con datos de una muestra de la comunidad UCE "
            f"(n={n_survey:,}). Los resultados son orientativos, exploratorios y no deben generalizarse "
            "sin validación externa. La clasificación se interpreta como apoyo analítico para la tesis, "
            "no como predicción causal del comportamiento electoral."
        ),
        color="yellow",
    )

def _render_kpi_row(summary_df: pd.DataFrame, n_survey: int) -> None:
    df = _normalize_metrics_df(summary_df)

    if "Configuración" in df.columns:
        mask = df["Configuración"].astype(str).eq(MAIN_CONFIG)
    else:
        mask = pd.Series(False, index=df.index)

    main_df = df.loc[mask].copy()

    if main_df.empty:
        main_df = df.copy()

    best = _get_best_model(df, preferred_config=MAIN_CONFIG)

    def avg(metric: str) -> str:
        if metric not in main_df.columns:
            return "N/D"
        return _fmt_float(pd.to_numeric(main_df[metric], errors="coerce").mean())

    best_model = best.get("Modelo", "N/D") if best is not None else "N/D"

    best_sub = "Config. no disponible"
    if best is not None:
        best_sub = f"{best.get('Configuración', MAIN_CONFIG)} · AUC {_fmt_float(best.get('AUC_OvR'))}"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Mejor modelo final",
            str(best_model),
            best_sub,
            "blue",
        )

    with c2:
        kpi_card(
            "AUC (OvR)",
            avg("AUC_OvR"),
            f"Promedio · config. {MAIN_CONFIG}",
            "green",
        )

    with c3:
        kpi_card(
            "Exactitud",
            avg("Accuracy"),
            f"Promedio · config. {MAIN_CONFIG}",
            "yellow",
        )

    with c4:
        kpi_card(
            "Kappa cuadrático",
            avg("QWK"),
            f"n = {n_survey:,} encuestas",
            "red",
        )


def _render_model_comparison(summary_df: pd.DataFrame) -> None:
    df = _normalize_metrics_df(summary_df)

    if df.empty:
        empty_state("No se encontraron métricas resumidas de modelos.")
        return

    metrics = _available_metrics(df)
    configs = _config_options(df)

    if not metrics:
        empty_state("No existen columnas métricas suficientes para comparar modelos.")
        return

    header_left, header_right = st.columns([1.35, 0.75], vertical_alignment="center")

    with header_left:
        _render_html(
            _compact_html(
                """
                <div class="section-title-card">Comparación de modelos</div>
                <div class="section-subtitle-card">
                    Rendimiento por algoritmo según métrica y configuración seleccionada.
                </div>
                """
            )
        )

    with header_right:
        selected_config = _single_select_control(
            "Configuración",
            configs,
            MAIN_CONFIG if MAIN_CONFIG in configs else configs[0],
            key="mp_config_selector_v3",
            label_visibility="collapsed",
        ) if configs else None

    metric_cols = st.columns([0.16, 0.84], vertical_alignment="center")

    with metric_cols[0]:
        st.markdown("**Métrica:**")

    with metric_cols[1]:
        selected_metric = _single_select_control(
            "Métrica",
            metrics,
            "AUC_OvR" if "AUC_OvR" in metrics else metrics[0],
            key="mp_metric_selector_v3",
            format_func=_metric_label,
            label_visibility="collapsed",
        )

    st.caption(_metric_description(selected_metric))

    plot_df = df.copy()

    if selected_config and "Configuración" in plot_df.columns:
        plot_df = plot_df[plot_df["Configuración"].astype(str) == selected_config]

    if plot_df.empty:
        empty_state("No hay datos para la configuración seleccionada.")
        return

    plot_df[selected_metric] = pd.to_numeric(plot_df[selected_metric], errors="coerce")
    plot_df = plot_df.dropna(subset=[selected_metric])

    if plot_df.empty:
        empty_state("La métrica seleccionada no tiene valores disponibles.")
        return

    plot_df = plot_df.sort_values(selected_metric, ascending=True)

    colors = [
        MODEL_COLORS.get(str(model), "#64748b")
        for model in plot_df["Modelo"]
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=plot_df[selected_metric],
            y=plot_df["Modelo"],
            orientation="h",
            marker=dict(color=colors),
            text=[_fmt_float(v) for v in plot_df[selected_metric]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                + _metric_label(selected_metric)
                + ": %{x:.3f}<extra></extra>"
            ),
        )
    )

    vmin = float(plot_df[selected_metric].min())
    vmax = float(plot_df[selected_metric].max())

    if selected_metric == "QWK":
        x_min = 0
        x_max = max(0.32, vmax * 1.22)
    else:
        x_min = max(0, min(0, vmin - 0.06))
        x_max = min(1.02, max(vmax + 0.08, vmax * 1.18))

    fig.update_layout(
        xaxis=dict(
            title="",
            range=[x_min, x_max],
            showgrid=True,
            gridcolor="#e5e7eb",
            zeroline=False,
            tickfont=dict(color="#94a3b8"),
        ),
        yaxis=dict(
            title="",
            automargin=True,
            tickfont=dict(color="#64748b", size=12),
        ),
        showlegend=False,
        bargap=0.25,
    )

    _plotly_base_layout(
        fig,
        height=315,
        margin=dict(l=8, r=40, t=10, b=15),
    )

    chart_config = {
        **PLOTLY_CONFIG,
        "displayModeBar": False,
        "responsive": True,
    }

    st.plotly_chart(fig, use_container_width=True, config=chart_config)

    legend_html = "".join(
        f"""
        <span style="display:inline-flex;align-items:center;margin-right:1rem;font-size:.78rem;color:#475569;">
            <span style="width:.75rem;height:.75rem;border-radius:.18rem;background:{MODEL_COLORS.get(m, '#64748b')};display:inline-block;margin-right:.35rem;"></span>
            {m}
        </span>
        """
        for m in _model_options(df)
    )

    _render_html(
        _compact_html(
            f"""
            <div style="display:flex;flex-wrap:wrap;gap:.15rem;margin-top:.35rem;">
                {legend_html}
            </div>
            """
        )
    )

def _render_config_comparison(summary_df: pd.DataFrame) -> None:
    df = _normalize_metrics_df(summary_df)
    if df.empty:
        empty_state("No existen métricas para comparar 3 y 5 niveles.")
        return

    metrics = _available_metrics(df)
    if not metrics or "Configuración" not in df.columns:
        empty_state("No hay métricas/configuraciones suficientes para generar el radar.")
        return

    models = _model_options(df)
    default_models = [m for m in ["Gradient Boosting", "Random Forest"] if m in models]
    if not default_models and models:
        default_models = models[:2]

    selected_models = st.multiselect(
        "Modelos visibles",
        models,
        default=default_models,
        key="mp_radar_models",
        help="Se recomienda comparar máximo dos o tres modelos para mantener legible el gráfico.",
    )

    if not selected_models:
        st.info("Selecciona al menos un modelo para comparar configuraciones.")
        return

    categories = [_metric_label(m) for m in metrics]
    fig = go.Figure()

    for model in selected_models:
        for config in CONFIG_ORDER:
            row = df[
                (df["Modelo"].astype(str) == model)
                & (df["Configuración"].astype(str) == config)
            ]

            if row.empty:
                continue

            values = []
            for metric in metrics:
                value = pd.to_numeric(row.iloc[0].get(metric), errors="coerce")
                values.append(float(value) if pd.notna(value) else None)

            values_closed = values + values[:1]
            cats_closed = categories + categories[:1]
            color = MODEL_COLORS.get(model, "#64748b")

            fig.add_trace(
                go.Scatterpolar(
                    r=values_closed,
                    theta=cats_closed,
                    mode="lines+markers",
                    name=f"{model} ({'3N' if config == '3 niveles' else '5N'})",
                    line=dict(
                        color=color,
                        width=2.7 if config == MAIN_CONFIG else 1.7,
                        dash="solid" if config == MAIN_CONFIG else "dash",
                    ),
                    marker=dict(size=6),
                    fill="toself" if config == MAIN_CONFIG else None,
                    opacity=0.88 if config == MAIN_CONFIG else 0.58,
                    hovertemplate="<b>%{fullData.name}</b><br>%{theta}: %{r:.3f}<extra></extra>",
                )
            )

    metric_values = df[metrics].apply(pd.to_numeric, errors="coerce").stack().dropna()

    if metric_values.empty:
        radial_min, radial_max = 0, 1
    else:
        radial_min = max(0, float(metric_values.min()) - 0.05)
        radial_max = min(1.05, float(metric_values.max()) + 0.08)


    fig.update_layout(
    polar=dict(
        bgcolor="#ffffff",
        radialaxis=dict(
            visible=True,
            range=[radial_min, radial_max],
            tickfont=dict(size=9, color="#94a3b8"),
            gridcolor="#e5e7eb",
        ),
        angularaxis=dict(
            tickfont=dict(size=11, color="#64748b"),
            gridcolor="#e5e7eb",
        ),
    ),
    legend=dict(
        orientation="h",
        y=-0.15,
        x=0.5,
        xanchor="center",
        font=dict(size=10),
        ),
    )

    _plotly_base_layout(fig, height=315, margin=dict(l=15, r=15, t=10, b=30))
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    conclusion = _build_config_conclusion(df)
    _render_html(
        _compact_html(
            f"""
            <div class="mp-insight">
                <strong>Conclusión:</strong> {conclusion}
            </div>
            """
        )
    )

def _build_config_conclusion(df: pd.DataFrame) -> str:
    if "Configuración" not in df.columns or "AUC_OvR" not in df.columns:
        return (
            "La comparación permite revisar el efecto de la granularidad de la variable objetivo, "
            "manteniendo como referencia principal la clasificación en 5 niveles."
        )

    avg = df.groupby("Configuración")["AUC_OvR"].mean(numeric_only=True)

    if {"3 niveles", "5 niveles"}.issubset(set(avg.index)):
        diff = avg.loc["5 niveles"] - avg.loc["3 niveles"]

        if diff >= 0:
            return (
                f"La configuración principal de <strong>5 niveles</strong> presenta una diferencia "
                f"promedio de AUC de <strong>{diff:+.3f}</strong> frente a 3 niveles. "
                "Esto respalda mantener la escala ordinal completa para reportar los resultados finales."
            )

        return (
            f"La configuración de 3 niveles muestra una ventaja promedio de AUC de "
            f"<strong>{abs(diff):.3f}</strong>; sin embargo, los resultados principales se mantienen "
            "en <strong>5 niveles</strong> porque conservan mayor detalle ordinal sobre la confianza electoral."
        )

    return (
        "La comparación entre configuraciones se utiliza como validación complementaria. "
        "La interpretación principal del módulo corresponde a 5 niveles."
    )

def _prepare_feature_df(feature_df: pd.DataFrame) -> pd.DataFrame:
    if feature_df is None or feature_df.empty:
        return pd.DataFrame()
    df = feature_df.copy()
    rename = {}
    for col in df.columns:
        c = str(col).strip().lower()
        if c in {"feature", "variable", "predictor"}:
            rename[col] = "Variable"
        elif c in {"label", "etiqueta"}:
            rename[col] = "Etiqueta"
        elif c in {"importance", "importancia"}:
            rename[col] = "Importancia"
        elif c in {"importancia_pct", "importance_pct", "porcentaje"}:
            rename[col] = "Importancia_pct"
    df = df.rename(columns=rename)
    if "Variable" not in df.columns and len(df.columns) > 0:
        df = df.rename(columns={df.columns[0]: "Variable"})
    if "Importancia_pct" not in df.columns:
        if "Importancia" in df.columns:
            val = pd.to_numeric(df["Importancia"], errors="coerce")
            df["Importancia_pct"] = val * 100 if val.max(skipna=True) <= 1.5 else val
        else:
            df["Importancia_pct"] = 0
    df["Importancia_pct"] = pd.to_numeric(df["Importancia_pct"], errors="coerce").fillna(0)
    if "Etiqueta" not in df.columns:
        df["Etiqueta"] = df["Variable"].astype(str).str.replace("_", " ").str.capitalize()
    return df.sort_values("Importancia_pct", ascending=False)

def _short_label(value: str, max_len: int = 58) -> str:
    text = str(value or "").strip()
    return text if len(text) <= max_len else text[: max_len - 1] + "…"

def _render_feature_importance(feature_df: pd.DataFrame) -> None:
    df = _prepare_feature_df(feature_df)
    if df.empty:
        empty_state("No se encontró el archivo feature_importance_latest.csv.")
        return

    left, right = st.columns([1, 1], vertical_alignment="center")
    with left:
        st.markdown("**Top de variables**")
    with right:
        options = [n for n in [5, 8, 11] if n <= len(df)]
        if not options:
            options = [min(5, len(df))]
        default_index = options.index(8) if 8 in options else 0
        top_n = st.radio("Mostrar top", options, index=default_index, horizontal=True, label_visibility="collapsed", key="mp_feature_top")

  
    data = df.head(int(top_n)).copy()
    data["Etiqueta_corta"] = data["Etiqueta"].apply(lambda x: _short_label(x, 58))
    data = data.sort_values("Importancia_pct", ascending=True)
    colors = px.colors.sample_colorscale("Blues", [0.45 + 0.45 * i / max(len(data) - 1, 1) for i in range(len(data))])

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=data["Importancia_pct"],
            y=data["Etiqueta_corta"],
            orientation="h",
            marker=dict(color=colors),
            text=[f"{v:.1f}%" for v in data["Importancia_pct"]],
            textposition="outside",
            customdata=data["Etiqueta"],
            hovertemplate="<b>%{y}</b><br>Importancia: %{x:.2f}%<extra></extra>",
        )
    )
    max_val = float(data["Importancia_pct"].max()) if not data.empty else 1
    fig.update_layout(
        xaxis=dict(title="", range=[0, max_val * 1.23], tickformat=".0f", showgrid=True, gridcolor="#eef2f7", ticksuffix="%"),
        yaxis=dict(title="", automargin=True),
        showlegend=False,
    )
    _plotly_base_layout(fig, height=max(310, int(top_n) * 42 + 90), margin=dict(l=5, r=65, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    top3 = df.head(3)
    top3_sum = top3["Importancia_pct"].sum()

    cards = []

    for _, row in top3.iterrows():
        rank = len(cards) + 1
        label = _esc(row.get("Etiqueta", row.get("Variable", "Variable")))
        pct = float(row.get("Importancia_pct", 0))

        cards.append(
            _compact_html(
                f"""
                <div class="mp-rank-card">
                    <span class="mp-rank-badge">{rank}</span>
                    <div>
                        <div class="mp-rank-title">{label}</div>
                        <div class="mp-rank-sub">{pct:.1f}% de importancia</div>
                    </div>
                </div>
                """
            )
        )

    cards.append(
        _compact_html(
            f"""
            <div class="mp-insight">
                Las tres variables principales concentran <strong>{top3_sum:.1f}%</strong>
                del peso relativo estimado del modelo. Esta lectura es asociativa, no causal.
            </div>
            """
        )
    )

    _render_html(
        _compact_html(
            f"""
            <div class="mp-mini-grid">
                {''.join(cards)}
            </div>
            """
        )
    )


def _matrix_order(labels: Iterable[str], config: str) -> list[str]:
    labels = [str(x) for x in labels]
    preferred = LEVELS_3 if config == "3 niveles" else LEVELS_5
    ordered = [x for x in preferred if x in labels]
    ordered.extend([x for x in labels if x not in ordered])
    return ordered


def _cell_color(value: float, max_val: float, is_diag: bool) -> tuple[str, str]:
    if max_val <= 0:
        max_val = 1
    intensity = max(0, min(float(value) / max_val, 1))
    if is_diag:
        # verde más intenso en la diagonal
        r = int(20 - 4 * intensity)
        g = int(180 - 45 * intensity)
        b = int(135 - 20 * intensity)
        return f"rgb({r},{g},{b})", "#ffffff"
    # violeta/rosado suave para errores
    r = int(254 - 48 * intensity)
    g = int(242 - 60 * intensity)
    b = int(242 - 32 * intensity)
    return f"rgb({r},{g},{b})", "#334155"


def _render_confusion_matrix(cm_df: pd.DataFrame, config: str) -> None:
    if cm_df is None or cm_df.empty:
        empty_state("No se encontró matriz de confusión para esta configuración.")
        return

    df = cm_df.copy()
    rename = {}
    for col in df.columns:
        c = str(col).lower().strip()
        if c in {"real", "clase real", "true", "actual"}:
            rename[col] = "Real"
        elif c in {"predicho", "clase predicha", "predicted", "pred"}:
            rename[col] = "Predicho"
        elif c in {"cantidad", "count", "n", "valor"}:
            rename[col] = "Cantidad"
    df = df.rename(columns=rename)

    required = {"Real", "Predicho", "Cantidad"}
    if not required.issubset(df.columns):
        empty_state("La matriz de confusión no tiene columnas Real, Predicho y Cantidad.")
        return

    df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce").fillna(0).astype(int)
    labels = _matrix_order(sorted(set(df["Real"].astype(str)) | set(df["Predicho"].astype(str))), config)
    pivot = (
        df.pivot_table(index="Real", columns="Predicho", values="Cantidad", aggfunc="sum", fill_value=0)
        .reindex(index=labels, columns=labels, fill_value=0)
    )
    total = int(pivot.values.sum())
    correct = int(sum(pivot.loc[label, label] for label in labels if label in pivot.index and label in pivot.columns))
    accuracy = correct / total if total else 0
    max_val = float(pivot.values.max()) if total else 1

    rows_html = []
    header = "<tr><td></td>" + "".join(f"<th>{label}</th>" for label in labels) + "</tr>"
    for real in labels:
        cells = [f"<td class='real-label'>{real}</td>"]
        for pred in labels:
            val = int(pivot.loc[real, pred])
            pct = (val / total * 100) if total else 0
            bg, fg = _cell_color(val, max_val, real == pred)
            cells.append(
                f"<td class='cell' style='background:{bg};color:{fg};' title='Real: {real} | Predicho: {pred} | n={val}'>"
                f"<span class='mp-cell-count'>{val}</span><span class='mp-cell-pct'>{pct:.1f}%</span></td>"
            )
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    html = f"""
    <div class='mp-matrix-wrap'>
        <div class='mp-matrix-title'>Clase predicha →</div>
        <table class='mp-matrix'>{header}{''.join(rows_html)}</table>
        <div class='mp-legend-row'>
            <span><span class='mp-swatch' style='background:#109981;'></span>Predicciones correctas (diagonal)</span>
            <span><span class='mp-swatch' style='background:#f5e8f5;'></span>Predicciones incorrectas</span>
            <span class='mp-accuracy'>Accuracy: {accuracy * 100:.1f}%</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    render_note(
        f"Lectura: la diagonal principal concentra los aciertos del modelo. En la configuración de {config}, "
        f"el modelo clasifica correctamente el {_fmt_pct(accuracy)} de los casos evaluados. "
        "En cinco niveles, esta métrica debe interpretarse junto con AUC, F1 ponderado y Kappa, debido a la mayor granularidad ordinal de la variable objetivo.",
        color="yellow",
    )


def _first_1d_column(df: pd.DataFrame, column_name: str) -> pd.Series:
    """Devuelve una Serie aunque existan columnas duplicadas tras renombrar aliases."""
    data = df.loc[:, df.columns == column_name]
    if data.empty:
        return pd.Series(index=df.index, dtype="float64")
    if isinstance(data, pd.Series):
        return data
    # Cuando hay columnas duplicadas, pandas devuelve un DataFrame.
    # Se toma la primera columna con datos válidos; si ninguna tiene datos, la primera.
    for col_pos in range(data.shape[1]):
        candidate = data.iloc[:, col_pos]
        if candidate.notna().any():
            return candidate
    return data.iloc[:, 0]


def _normalize_seed_df(seed_df: pd.DataFrame) -> pd.DataFrame:
    if seed_df is None or seed_df.empty:
        return pd.DataFrame()

    df = seed_df.copy()

    normalized_columns: list[str] = []
    for col in df.columns:
        c = str(col).strip()
        lower = c.lower()
        if lower in {"modelo", "model"}:
            normalized_columns.append("Modelo")
        elif lower in {"configuración", "configuracion", "config"}:
            normalized_columns.append("Configuración")
        elif lower in {"seed", "semilla"}:
            normalized_columns.append("Seed")
        elif c in {"AUC OvR", "AUC", "AUC (OvR)", "AUC_OvR"}:
            normalized_columns.append("AUC_OvR")
        elif c in {"Accuracy", "Exactitud"}:
            normalized_columns.append("Accuracy")
        elif c in {"F1 ponderado", "F1 Ponderado", "F1_ponderado"}:
            normalized_columns.append("F1_ponderado")
        elif c in {"Kappa cuadrático (QWK)", "Kappa Cuadrático (QWK)", "QWK"}:
            normalized_columns.append("QWK")
        else:
            normalized_columns.append(c)

    df.columns = normalized_columns

    clean = pd.DataFrame(index=df.index)
    for base_col in ["Modelo", "Configuración", "Seed", *METRIC_ORDER]:
        if base_col in df.columns:
            clean[base_col] = _first_1d_column(df, base_col)

    # Conserva columnas auxiliares sin duplicarlas.
    for col in df.columns:
        if col not in clean.columns and col not in ["Modelo", "Configuración", "Seed", *METRIC_ORDER]:
            clean[col] = _first_1d_column(df, col)

    for metric in METRIC_ORDER:
        if metric in clean.columns:
            clean[metric] = pd.to_numeric(clean[metric], errors="coerce")
    if "Seed" in clean.columns:
        clean["Seed"] = pd.to_numeric(clean["Seed"], errors="coerce")

    return clean


def _cv(values: pd.Series) -> tuple[float, float, float]:
    vals = pd.to_numeric(values, errors="coerce").dropna()
    if vals.empty:
        return 0, 0, 0
    mean = float(vals.mean())
    std = float(vals.std(ddof=0))
    return mean, std, std / mean if mean else 0


def _render_seed_stability(seed_df: pd.DataFrame) -> None:
    df = _normalize_seed_df(seed_df)
    if df.empty:
        empty_state("No se encontraron métricas por semilla.")
        return

    if not {"Modelo", "Configuración", "Seed"}.issubset(df.columns):
        empty_state("El archivo de estabilidad no tiene Modelo, Configuración y Seed.")
        return

    models = _model_options(df)
    configs = _config_options(df)
    metrics = _available_metrics(df)
    if not models or not configs or not metrics:
        empty_state("No hay suficientes datos para graficar estabilidad por semilla.")
        return

    c1, c2, c3 = st.columns([1, 1, 1.4])
    with c1:
        selected_model = st.selectbox("Modelo", models, index=models.index("Random Forest") if "Random Forest" in models else 0, key="mp_seed_model_v2")
    with c2:
        selected_config = st.selectbox(
            "Configuración",
            configs,
            index=configs.index(MAIN_CONFIG) if MAIN_CONFIG in configs else 0,
            key="mp_seed_config_v2",
        )
    with c3:
        default_metrics = [m for m in METRIC_ORDER if m in metrics]
        selected_metrics = st.multiselect(
            "Métricas visibles",
            metrics,
            default=default_metrics or metrics[:1],
            format_func=_metric_label,
            key="mp_seed_metrics_v2",
        )



    filtered = df[(df["Modelo"].astype(str) == selected_model) & (df["Configuración"].astype(str) == selected_config)].copy()
    if filtered.empty:
        empty_state("No hay datos para la combinación seleccionada.")
        return

    filtered = filtered.dropna(subset=["Seed"]).sort_values("Seed")

    selected_metrics = [m for m in selected_metrics if m in filtered.columns]

    if not selected_metrics:
        empty_state("Selecciona al menos una métrica para visualizar la estabilidad.")
        return

    fig = go.Figure()

    line_colors = {
        "AUC_OvR": "#3b82f6",
        "Accuracy": "#10b981",
        "F1_ponderado": "#f59e0b",
        "QWK": "#ef4444",
    }

    valid_series = []
    partial_metrics = []

    for metric in selected_metrics:
        y = pd.to_numeric(filtered[metric], errors="coerce")
        valid_count = int(y.notna().sum())

        if valid_count == 0:
            partial_metrics.append(f"{_metric_label(metric)}: sin valores válidos")
            continue

        if valid_count < len(filtered):
            partial_metrics.append(
                f"{_metric_label(metric)}: {valid_count}/{len(filtered)} semillas con dato"
            )

        valid_series.append(y)

        fig.add_trace(
            go.Scatter(
                x=filtered["Seed"],
                y=y,
                mode="lines+markers",
                connectgaps=True,
                name=_metric_label(metric),
                line=dict(color=line_colors.get(metric, "#64748b"), width=2.4),
                marker=dict(size=7),
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Semilla: %{x}<br>"
                    "Valor: %{y:.3f}"
                    "<extra></extra>"
                ),
            )
        )

    if not fig.data:
        empty_state("Las métricas seleccionadas no tienen valores válidos para graficar.")
        return

    all_values = pd.concat(valid_series).dropna()

    if all_values.empty:
        y_low, y_high = 0, 1
    else:
        vmin = float(all_values.min())
        vmax = float(all_values.max())
        pad = max(0.04, (vmax - vmin) * 0.16)

        # QWK puede estar por debajo de 0; las demás métricas suelen estar entre 0 y 1.
        y_low = max(-1.0, min(0.0, vmin - pad))
        y_high = min(1.05, max(0.85, vmax + pad))

    seed_min = float(filtered["Seed"].min())
    seed_max = float(filtered["Seed"].max())
    x_pad = max(1.0, (seed_max - seed_min) * 0.05)

    fig.add_hline(
        y=0.8,
        line_dash="dash",
        line_color="#e2e8f0",
        annotation_text="Referencia 0.80",
        annotation_position="top right",
    )

    fig.update_layout(
        dragmode="zoom",
        hovermode="x unified",
        uirevision=f"{selected_model}-{selected_config}",
        xaxis=dict(
            title="Semilla",
            showgrid=True,
            gridcolor="#eef2f7",
            range=[seed_min - x_pad, seed_max + x_pad],
            fixedrange=False,
        ),
        yaxis=dict(
            title="Valor de la métrica",
            range=[y_low, y_high],
            showgrid=True,
            gridcolor="#eef2f7",
            fixedrange=False,
        ),
        legend=dict(
            orientation="h",
            y=1.12,
            x=0,
            font=dict(size=10),
        ),
    )

    _plotly_base_layout(fig, height=390, margin=dict(l=10, r=20, t=42, b=35))

    stability_config = {
        **PLOTLY_CONFIG,
        "displayModeBar": False,
        "displaylogo": False,
        "scrollZoom": True,
        "responsive": True,
        "staticPlot": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    }

    st.plotly_chart(fig, use_container_width=True, config=stability_config)

    if partial_metrics:
        st.caption("Nota de datos: " + " · ".join(partial_metrics))



    stat_cards = []
    for metric in metrics:
        mean, std, coef = _cv(filtered[metric])
        color = "#059669" if coef < 0.02 else "#d97706"
        width = min(coef * 1100, 100)

        stat_cards.append(
            _compact_html(
                f"""
                <div class='mp-soft-card'>
                    <div style='font-size:.76rem;color:#64748b;font-weight:800;'>{_metric_label(metric)}</div>
                    <div style='font-size:1.15rem;color:#0f172a;font-weight:900;margin-top:.2rem;'>{mean:.3f}</div>
                    <div style='display:flex;gap:.7rem;margin-top:.35rem;font-size:.73rem;color:#64748b;'>
                        <span>σ = {std:.4f}</span>
                        <span style='color:{color};font-weight:900;'>CV = {coef*100:.2f}%</span>
                    </div>
                    <div class='mp-progress' style='margin-top:.55rem;'>
                        <span style='width:{width:.1f}%;background:{color};'></span>
                    </div>
                </div>
                """
            )
        )
    
    _render_html(
        _compact_html(
            f"""
            <div class='mp-stability-grid'>
                {''.join(stat_cards)}
            </div>
            """
        )
    )

    render_note(
        "Interpretación: la estabilidad se evalúa observando la variación de las métricas ante diferentes particiones train/test. "
        "El AUC conserva un comportamiento relativamente consistente, mientras que exactitud, F1 y especialmente Kappa pueden variar más por la granularidad de cinco niveles y el tamaño de algunas clases. "
        "Por ello, esta validación se interpreta como control de robustez exploratorio, no como garantía de generalización externa.",
        color="yellow",
    )


def _rule_color(prediction: str) -> tuple[str, str, str]:
    p = str(prediction).lower()
    if "alta" in p and "baja" not in p:
        return "#ecfdf5", "#047857", "#a7f3d0"
    if "baja" in p:
        return "#fef2f2", "#b91c1c", "#fecaca"
    return "#eff6ff", "#1d4ed8", "#bfdbfe"


def _normalize_rules_df(rules_df: pd.DataFrame) -> pd.DataFrame:
    if rules_df is None or rules_df.empty:
        return pd.DataFrame()
    df = rules_df.copy()
    rename = {}
    for col in df.columns:
        c = str(col).strip().lower()
        if c in {"condicion", "condición", "condition"}:
            rename[col] = "Condición"
        elif c in {"prediction", "prediccion", "predicción", "clase"}:
            rename[col] = "Predicción"
        elif c in {"support", "soporte"}:
            rename[col] = "Soporte"
        elif c in {"confidence", "confianza"}:
            rename[col] = "Confianza"
        elif c in {"description", "descripcion", "descripción", "lectura"}:
            rename[col] = "Descripción"
        elif c in {"bloque", "regla"}:
            rename[col] = "Regla"
    df = df.rename(columns=rename)
    # Compatibilidad con el formato anterior Bloque/Lectura.
    if "Condición" not in df.columns and "Regla" in df.columns:
        df["Condición"] = df["Regla"].astype(str)
    if "Predicción" not in df.columns:
        df["Predicción"] = "Lectura técnica"
    if "Descripción" not in df.columns:
        df["Descripción"] = ""
    if "Soporte" not in df.columns:
        df["Soporte"] = 0
    if "Confianza" not in df.columns:
        df["Confianza"] = 0
    if "Grupo" not in df.columns:
        df["Grupo"] = "Predictor"
    if "Descripcion" not in df.columns:
        df["Descripcion"] = ""    
    return df


def _render_interpretation_rules(rules_df: pd.DataFrame) -> None:
    df = _normalize_rules_df(rules_df)

    if df.empty:
        empty_state("No se encontraron reglas de interpretación técnica.")
        return

    cards = []

    for idx, row in df.head(4).reset_index(drop=True).iterrows():
        prediction = str(row.get("Predicción", "Lectura exploratoria"))
        condition = str(row.get("Condición", "Condición no disponible"))
        description = str(row.get("Descripción", "Sin descripción disponible."))

        support = pd.to_numeric(row.get("Soporte", 0), errors="coerce")
        confidence = pd.to_numeric(row.get("Confianza", 0), errors="coerce")

        support = 0 if pd.isna(support) else float(support)
        confidence = 0 if pd.isna(confidence) else float(confidence)

        bg, fg, border = _rule_color(prediction)


        cards.append(
            _compact_html(
                f"""
                <div class="mp-rule-card">
                    <div class="mp-rule-head">
                        <span class="mp-rule-num">{idx + 1}</span>
                        <span class="mp-rule-chip" style="background:{bg};color:{fg};border-color:{border};">
                            {_esc(prediction)}
                        </span>
                    </div>

                    <div class="mp-rule-code">{_esc(condition)}</div>

                    <div class="mp-rule-desc">{_esc(description)}</div>

                    <div class="mp-rule-meta">
                        <span>Soporte<br><strong style="color:#334155;">{support * 100:.1f}%</strong></span>
                        <span>Confianza<br><strong style="color:#334155;">{confidence * 100:.1f}%</strong></span>
                        <span class="mp-progress">
                            <span style="width:{min(confidence * 100, 100):.1f}%;"></span>
                        </span>
                    </div>
                </div>
                """
            )
        )

    _render_html(
        _compact_html(
            f"""
            <div class="mp-rule-grid">
                {''.join(cards)}
            </div>
            """
        )
    )

    render_note(
        "Estas reglas son lecturas asociativas derivadas de las variables influyentes del modelo. No representan causalidad.",
        color="blue",
    )



def _prepare_schema_df(schema_df: pd.DataFrame, feature_df: pd.DataFrame) -> pd.DataFrame:
    if schema_df is not None and not schema_df.empty:
        df = schema_df.copy()
    else:
        features = _prepare_feature_df(feature_df).head(7)
        rows = []
        for _, row in features.iterrows():
            var = str(row.get("Variable", row.get("Etiqueta", "variable")))
            label = str(row.get("Etiqueta", var.replace("_", " ").capitalize()))
            rows.append({
                "Variable": var,
                "Etiqueta": label,
                "Tipo": "escala",
                "Min": 1,
                "Max": 5,
                "Paso": 1,
                "Opciones": "1|2|3|4|5",
                "Valor_por_defecto": 3,
                "Peso": float(row.get("Importancia_pct", 0)) / 100,
            })
        df = pd.DataFrame(rows)

    rename = {}
    for col in df.columns:
        c = str(col).strip().lower()
        if c in {"feature", "variable"}:
            rename[col] = "Variable"
        elif c in {"label", "etiqueta"}:
            rename[col] = "Etiqueta"
        elif c in {"type", "tipo"}:
            rename[col] = "Tipo"
        elif c in {"options", "opciones"}:
            rename[col] = "Opciones"
        elif c in {"default", "valor_por_defecto", "valor por defecto"}:
            rename[col] = "Valor_por_defecto"
        elif c in {"min", "mín", "minimo", "mínimo"}:
            rename[col] = "Min"
        elif c in {"max", "máx", "maximo", "máximo"}:
            rename[col] = "Max"
        elif c in {"step", "paso"}:
            rename[col] = "Paso"
        elif c in {"weight", "peso", "importancia"}:
            rename[col] = "Peso"
    df = df.rename(columns=rename)
    if "Etiqueta" not in df.columns and "Variable" in df.columns:
        df["Etiqueta"] = df["Variable"].astype(str).str.replace("_", " ").str.capitalize()
    if "Peso" not in df.columns:
        df["Peso"] = 1 / max(len(df), 1)
    df["Peso"] = pd.to_numeric(df["Peso"], errors="coerce").fillna(1 / max(len(df), 1))
   
    if "Grupo" not in df.columns:
        df["Grupo"] = "Predictor"

    if "Descripcion" not in df.columns:
        df["Descripcion"] = ""

    if "Tipo" not in df.columns:
        df["Tipo"] = "escala"

    if "Opciones" not in df.columns:
        df["Opciones"] = "1|2|3|4|5"

    if "Valor_por_defecto" not in df.columns:
        df["Valor_por_defecto"] = 3
    return df



def _score_simulator(values: dict, schema_df: pd.DataFrame) -> tuple[str, float, str]:
    """Respaldo pedagógico si el artefacto joblib no está disponible.

    La salida mantiene 5 niveles para conservar coherencia con el modelo final.
    """
    if not values or schema_df.empty:
        return "Sin estimación", 0.0, "#64748b"

    weighted = 0.0
    weight_sum = 0.0

    for _, row in schema_df.iterrows():
        var = row.get("Variable")
        if var not in values:
            continue

        weight = float(row.get("Peso", 1))
        value = values[var]
        tipo = str(row.get("Tipo", "")).lower()
        norm = 0.5

        if tipo in {"numérica", "numerica", "numeric"}:
            min_v = float(row.get("Min", 0) or 0)
            max_v = float(row.get("Max", 100) or 100)
            try:
                norm = (float(value) - min_v) / max(max_v - min_v, 1e-9)
            except Exception:
                norm = 0.5
        elif tipo in {"escala", "scale", "ordinal"}:
            try:
                min_v = float(row.get("Min", 1) or 1)
                max_v = float(row.get("Max", 5) or 5)
                norm = (float(value) - min_v) / max(max_v - min_v, 1e-9)
            except Exception:
                norm = 0.5
        elif tipo in {"binaria", "binary", "boolean"}:
            norm = 1.0 if str(value).strip().lower() in {"sí", "si", "yes", "1", "true"} else 0.0
        else:
            options = [x.strip() for x in str(row.get("Opciones", "")).split("|") if x.strip()]
            if options and str(value) in options:
                norm = options.index(str(value)) / max(len(options) - 1, 1)
            else:
                norm = 0.5

        weighted += norm * weight
        weight_sum += weight

    score = weighted / weight_sum if weight_sum else 0.5
    probability = max(0.18, min(0.94, 0.24 + score * 0.62))

    if score < 0.20:
        return "Muy baja confianza electoral", probability, "#dc2626"
    if score < 0.40:
        return "Baja confianza electoral", probability, "#ea580c"
    if score < 0.60:
        return "Confianza media electoral", probability, "#d97706"
    if score < 0.80:
        return "Alta confianza electoral", probability, "#059669"
    return "Muy alta confianza electoral", probability, "#047857"


def _schema_options(row: pd.Series) -> list[str]:
    options = [x.strip() for x in str(row.get("Opciones", "")).split("|") if x.strip()]
    default = str(row.get("Valor_por_defecto", "")).strip()
    if not options and default:
        options = [default]
    return options or ["No disponible"]


def _pick_option(options: list[str], preferred: list[str], default: str | None = None) -> str:
    normalized = {str(opt).strip().lower(): opt for opt in options}
    for item in preferred:
        key = str(item).strip().lower()
        if key in normalized:
            return normalized[key]
    if default and str(default) in options:
        return str(default)
    return options[0]


def _scenario_value(row: pd.Series, scenario: str) -> str:
    options = _schema_options(row)
    label = str(row.get("Etiqueta", row.get("Variable", ""))).lower()
    default = str(row.get("Valor_por_defecto", options[0]))
    scenario = str(scenario).lower()

    if "neutral" in scenario:
        return _pick_option(options, [default, "Ni de acuerdo ni en desacuerdo", "A veces", "Poco"], default)

    if "preocupación" in scenario or "preocupacion" in scenario:
        if "bots" in label:
            return _pick_option(options, ["Totalmente de acuerdo", "De acuerdo"], default)
        if "regulación" in label or "regulacion" in label:
            return _pick_option(options, ["Totalmente de acuerdo", "De acuerdo"], default)
        if "transparencia" in label or "comunicación" in label or "comunicacion" in label:
            return _pick_option(options, ["En desacuerdo", "Ni de acuerdo ni en desacuerdo"], default)
        if "influencia" in label or "voto" in label:
            return _pick_option(options, ["Sí, mucho", "Sí, algo"], default)
        if "verificación" in label or "verificacion" in label:
            return _pick_option(options, ["Siempre", "A veces"], default)

    if "confianza" in scenario or "transparencia" in scenario:
        if "bots" in label:
            return _pick_option(options, ["En desacuerdo", "Ni de acuerdo ni en desacuerdo"], default)
        if "transparencia" in label or "comunicación" in label or "comunicacion" in label:
            return _pick_option(options, ["De acuerdo", "Totalmente de acuerdo"], default)
        if "regulación" in label or "regulacion" in label:
            return _pick_option(options, ["De acuerdo", "Totalmente de acuerdo"], default)
        if "influencia" in label or "voto" in label:
            return _pick_option(options, ["Poco", "Nada"], default)

    if "baja transparencia" in scenario:
        if "transparencia" in label or "comunicación" in label or "comunicacion" in label:
            return _pick_option(options, ["Totalmente en desacuerdo", "En desacuerdo"], default)
        if "bots" in label or "regulación" in label or "regulacion" in label:
            return _pick_option(options, ["Totalmente de acuerdo", "De acuerdo"], default)
        if "influencia" in label or "voto" in label:
            return _pick_option(options, ["Sí, mucho", "Sí, algo"], default)

    if "verificación" in scenario or "verificacion" in scenario:
        if "verificación" in label or "verificacion" in label:
            return _pick_option(options, ["Siempre", "A veces"], default)
        if "bots" in label or "regulación" in label or "regulacion" in label:
            return _pick_option(options, ["De acuerdo", "Totalmente de acuerdo"], default)

    return _pick_option(options, [default], default)


def _scenario_slug(value: str) -> str:
    text = str(value).lower()
    repl = str.maketrans("áéíóúüñ", "aeiouun")
    text = text.translate(repl)
    return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_")


def _distribution_html(distribution: list[dict]) -> str:
    rows = []
    for item in distribution:
        label = _esc(item.get("class", "Clase"))
        prob = float(item.get("probability", 0) or 0)
        color = item.get("color", "#64748b")
        rows.append(
            f"""
            <div class='mp-dist-row'>
                <div class='mp-dist-head'>
                    <span>{label}</span>
                    <strong>{prob * 100:.0f}%</strong>
                </div>
                <div class='mp-dist-track'><span class='mp-dist-fill' style='width:{prob * 100:.1f}%;background:{color};'></span></div>
            </div>
            """
        )
    return _compact_html("".join(rows))


def _render_simulator_base(schema_df: pd.DataFrame, feature_df: pd.DataFrame) -> None:
    df = _prepare_schema_df(schema_df, feature_df)
    if df.empty:
        empty_state("No se encontró simulator_feature_schema.csv ni variables suficientes para construir el simulador.")
        return

    # El simulador expone solo variables interpretables. El modelo real usa defaults
    # para el resto de columnas del pipeline entrenado.
    df["Peso"] = pd.to_numeric(df.get("Peso", 0), errors="coerce").fillna(0)
    df = df.sort_values("Peso", ascending=False).head(6).reset_index(drop=True)

    render_note(
        "Este simulador usa el modelo final Random Forest con clasificación de 5 niveles. Presenta escenarios hipotéticos de confianza electoral; no predice comportamiento individual ni establece causalidad.",
        color="yellow",
    )

    scenarios = [
        "Perfil neutral",
        "Alta preocupación por IA",
        "Alta confianza/transparencia percibida",
        "Baja transparencia percibida",
        "Mayor verificación de fuentes",
    ]

    scenario = _single_select_control(
        "Escenario rápido",
        scenarios,
        "Perfil neutral",
        key="mp_sim_scenario_rf5",
        label_visibility="visible",
    )
    scenario_key = _scenario_slug(scenario)

    left, right = st.columns([1.65, 0.95], gap="medium")
    values: dict = {}
    submitted = False

    with left:
        _render_html(
            _compact_html(
                """
                <div class='mp-sim-context'>
                    Ajusta las variables principales del modelo. Las demás columnas requeridas por el pipeline se completan con valores representativos de la muestra.
                </div>
                """
            )
        )

        with st.form(f"mp_simulator_form_{scenario_key}", clear_on_submit=False):
            grid = st.columns(2)
            for i, row in df.iterrows():
                var = str(row.get("Variable", f"var_{i}"))
                label = str(row.get("Etiqueta", var))
                desc = str(row.get("Descripcion", ""))
                options = _schema_options(row)
                default_value = _scenario_value(row, scenario)
                default_idx = options.index(default_value) if default_value in options else 0

                with grid[i % 2]:
                    values[var] = st.selectbox(
                        label,
                        options,
                        index=default_idx,
                        help=desc if desc and desc.lower() != "nan" else None,
                        key=f"mp_sim_{scenario_key}_{i}",
                    )

            submitted = st.form_submit_button("Estimar escenario", type="primary")

    if submitted:
        result = predict_simulator(values)
        if result is None:
            st.session_state.pop("mp_sim_result_rf5", None)
            st.session_state.pop("mp_sim_values_rf5", None)
            st.session_state.pop("mp_sim_schema_rf5", None)

            st.warning(
            "No se encontró el pipeline entrenado del simulador. "
            "Verifica que el artefacto Random Forest de 5 niveles y los valores por defecto estén disponibles."
        )    
            
        else:
            st.session_state["mp_sim_result_rf5"] = result
            st.session_state["mp_sim_values_rf5"] = values
            st.session_state["mp_sim_schema_rf5"] = df[["Variable", "Etiqueta", "Grupo", "Peso"]].to_dict("records")


    result = st.session_state.get("mp_sim_result_rf5")
    saved_values = st.session_state.get("mp_sim_values_rf5", values)
    saved_schema = st.session_state.get("mp_sim_schema_rf5", df[["Variable", "Etiqueta", "Grupo", "Peso"]].to_dict("records"))

    with right:
        if result:
            color = result.get("color", "#64748b")
            label = result.get("label", "Sin estimación")
            prob = float(result.get("probability", 0) or 0)
            uses_real = bool(result.get("uses_real_model", False))
            metadata = result.get("metadata", {}) or {}
            model_name = metadata.get("modelo_final", "Random Forest")
            config_name = metadata.get("configuracion", "5 niveles")

            _render_html(
                _compact_html(
                    f"""
                    <div class='mp-result-card' style='border-color:{color}33;background:{color}0d;'>
                        <div class='mp-result-title'>Escenario estimado</div>
                        <div class='mp-result-value' style='color:{color};'>{_esc(label)}</div>
                        <div style='display:flex;justify-content:space-between;font-size:.78rem;color:#64748b;margin-bottom:.3rem;'>
                            <span>Probabilidad orientativa</span><strong>{prob * 100:.0f}%</strong>
                        </div>
                        <div class='mp-progress'><span style='background:{color};width:{prob * 100:.1f}%;'></span></div>
                        <div class='mp-method-mini'>
                            Modelo: <strong>{_esc(model_name)}</strong> · Configuración: <strong>{_esc(config_name)}</strong><br>
                            {'Pipeline entrenado disponible' if uses_real else 'Respaldo pedagógico sin joblib'}.
                        </div>
                    </div>
                    """
                )
            )

            distribution = result.get("distribution", []) or []
            if distribution:
                _render_html(
                    _compact_html(
                        f"""
                        <div class='mp-result-card' style='margin-top:1rem;'>
                            <div class='mp-result-title'>Distribución por clase</div>
                            {_distribution_html(distribution)}
                        </div>
                        """
                    )
                )
        else:
            _render_html(
                _compact_html(
                    """
                    <div class='mp-result-card'>
                        <div class='mp-result-title'>Escenario estimado</div>
                        <div style='font-size:.86rem;color:#94a3b8;font-style:italic;'>Selecciona un escenario, ajusta las variables y presiona "Estimar escenario".</div>
                    </div>
                    """
                )
            )

        schema_lookup = {str(row.get("Variable")): row for row in saved_schema}
        profile_html = ""
        for var, value in list(saved_values.items())[:6]:
            row = schema_lookup.get(str(var), {})
            label = row.get("Etiqueta", str(var).replace("_", " ").capitalize())
            profile_html += (
                f"<div style='display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.75rem;font-size:.76rem;margin:.45rem 0;'>"
                f"<span style='color:#94a3b8;line-height:1.25;'>{_esc(label)}</span>"
                f"<strong style='color:#334155;text-align:right;'>{_esc(value)}</strong></div>"
            )

        _render_html(
            _compact_html(
                f"""
                <div class='mp-result-card' style='margin-top:1rem;'>
                    <div class='mp-result-title'>Variables modificadas</div>
                    {profile_html}
                </div>
                """
            )
        )

    total_weight = float(pd.to_numeric(df["Peso"], errors="coerce").fillna(0).sum())
    chips = "".join(
        f"<span class='mp-sim-chip'>{_esc(row.get('Etiqueta'))}: {_fmt_pct(row.get('Peso', 0) / total_weight if total_weight else 0, 1)}</span>"
        for _, row in df.iterrows()
    )
    _render_html(
        _compact_html(
            f"""
            <div class='mp-sim-chip-row'>
                {chips}
            </div>
            """
        )
    )

    render_note(
        "Lectura metodológica: el simulador modifica solo variables seleccionadas por su importancia e interpretabilidad. El resto del vector de entrada permanece con valores por defecto calculados desde la base de entrenamiento.",
        color="blue",
    )


# -----------------------------------------------------------------------------
# Render principal
# -----------------------------------------------------------------------------


def render_modelos_predictivos(survey_df: pd.DataFrame) -> None:

    n_survey = _safe_count(survey_df)
    topbar(
        title="Modelos predictivos",
        subtitle=(
            "Clasificación exploratoria de cinco niveles de confianza electoral a partir de variables "
            "sociodemográficas, exposición a IA y percepción ciudadana."
        ),
        pill_text=f"n = {n_survey:,} encuestas" if n_survey else "encuestas no cargadas",
    )

    summary_df = _normalize_metrics_df(load_model_metrics_summary())
    seed_df = load_model_metrics_by_seed_dashboard()
    cm3_df = load_confusion_matrix_3_levels()
    cm5_df = load_confusion_matrix_5_levels()
    feature_df = load_feature_importance()
    interpretation_df = load_model_interpretation_rules()
    simulator_schema = load_simulator_feature_schema()

    if summary_df.empty:
        empty_state(
            "No se encontraron artefactos de modelos. Ejecuta: python src/07_dashboard_artifacts/build_model_dashboard_artifacts.py"
        )
        return

    _render_method_warning(n_survey)
    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    _render_kpi_row(summary_df, n_survey)
    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)


    col1, col2 = st.columns([1.18, 1], gap="medium")

    with col1:
        with st.container(key="card_mp_metricas"):
            _render_model_comparison(summary_df)

    with col2:
        with st.container(key="card_mp_configuracion"):
            render_card_header(
                "Validación complementaria 3 vs 5 niveles",
                "Comparación metodológica frente a la configuración principal de 5 niveles.",
            )
            _render_config_comparison(summary_df)         

    st.markdown('<div class="section-gap-small"></div>', unsafe_allow_html=True)

    tabs = st.tabs(
        [
            "Importancia de variables",
            "Matriz de confusión",
            "Estabilidad",
            "Simulador exploratorio",
        ]
    )

    with tabs[0]:
        with st.container(key="card_mp_importancia"):
            render_card_header(
                "Importancia de variables",
                "Contribución relativa de cada predictor al modelo final.",
            )
            _render_feature_importance(feature_df)

            with st.expander("Ver interpretación técnica del modelo"):
                _render_interpretation_rules(interpretation_df)

            with st.expander("Ver tabla completa de importancia"):
                st.dataframe(
                    _prepare_feature_df(feature_df),
                    use_container_width=True,
                    hide_index=True,
                    height=360,
                )    

    with tabs[1]:
        with st.container(key="card_mp_clases"):
            render_card_header(
                "Matriz de confusión",
                "Comparación entre predicciones del modelo y clases reales.",
            )
            selected_config = st.radio(
                "Configuración de confianza electoral",
                ["3 niveles", "5 niveles"],
                index=1,
                horizontal=True,
                label_visibility="collapsed",
                key="mp_confusion_config_v2",
            )
            active_cm = cm3_df if selected_config == "3 niveles" else cm5_df
            _render_confusion_matrix(active_cm, selected_config)
            with st.expander("Ver tabla de matriz de confusión"):
                st.dataframe(active_cm, use_container_width=True, hide_index=True, height=320)

    with tabs[2]:
        with st.container(key="card_mp_estabilidad"):
            render_card_header(
                "Estabilidad por semilla aleatoria",
                "Variación del rendimiento al cambiar la partición entrenamiento/prueba.",
            )
            _render_seed_stability(seed_df)
            with st.expander("Ver métricas por semilla"):
                st.dataframe(_normalize_seed_df(seed_df), use_container_width=True, hide_index=True, height=360)

    with tabs[3]:
        with st.container(key="card_mp_simulador_base"):
            render_card_header(
                "Simulador exploratorio de confianza electoral",
                "Prototipo interactivo basado en el modelo final Random Forest de 5 niveles.",
            )
            _render_simulator_base(simulator_schema, feature_df)

    st.caption(
        "Dashboard de tesis · Sistemas de Información · Universidad Central del Ecuador · Modelos exploratorios de confianza electoral."
    )
