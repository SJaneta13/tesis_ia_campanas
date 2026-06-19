# dashboard/common.py
import html
import pandas as pd
import streamlit as st
import plotly.express as px


PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}

BASE_COLORS = [
    "#2563eb",
    "#38bdf8",
    "#14b8a6",
    "#f59e0b",
    "#fb7185",
    "#94a3b8",
]

LIKERT_LABELS = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Ni de acuerdo ni en desacuerdo",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}

LIKERT_ORDER = list(LIKERT_LABELS.values())

LIKERT_COLORS = {
    "Totalmente en desacuerdo": "#1D4ED8",
    "En desacuerdo": "#93C5FD",
    "Ni de acuerdo ni en desacuerdo": "#CBD5E1",
    "De acuerdo": "#99F6E4",
    "Totalmente de acuerdo": "#14B8A6",
}


def find_first_existing_column(df: pd.DataFrame, candidates: list[str]):
    if df is None or df.empty:
        return None

    normalized = {str(c).lower().strip(): c for c in df.columns}

    for candidate in candidates:
        key = candidate.lower().strip()
        if key in normalized:
            return normalized[key]

    for col in df.columns:
        col_l = str(col).lower().strip()
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

def safe_text(value) -> str:
    return html.escape(str(value))

def safe_pct(count: int, total: int) -> float:
    if not total:
        return 0.0
    return round(count / total * 100, 1)


def likert_to_numeric(series: pd.Series) -> pd.Series:
    mapping = {
        "totalmente en desacuerdo": 1,
        "en desacuerdo": 2,
        "ni de acuerdo ni en desacuerdo": 3,
        "de acuerdo": 4,
        "totalmente de acuerdo": 5,
    }

    numeric = pd.to_numeric(series, errors="coerce")

    if numeric.notna().sum() > 0:
        return numeric.round()

    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .map(mapping)
    )


def make_category_distribution(
    df: pd.DataFrame,
    col: str,
    label_name: str,
    order: list[str] | None = None,
) -> pd.DataFrame:
    if df is None or df.empty or not col or col not in df.columns:
        return pd.DataFrame(columns=[label_name, "Cantidad", "Porcentaje"])

    values = clean_category_series(df[col])
    counts = values.value_counts()

    if order:
        ordered_index = [item for item in order if item in counts.index]
        remaining_index = [item for item in counts.index if item not in ordered_index]
        counts = counts.reindex(ordered_index + remaining_index)

    out = counts.reset_index()
    out.columns = [label_name, "Cantidad"]

    total = out["Cantidad"].sum()
    if total == 0:
        return pd.DataFrame(columns=[label_name, "Cantidad", "Porcentaje"])

    out["Porcentaje"] = (out["Cantidad"] / total * 100).round(1)
    return out


def make_likert_distribution(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if df is None or df.empty or not col or col not in df.columns:
        return pd.DataFrame(columns=["Respuesta", "Cantidad", "Porcentaje"])

    values = likert_to_numeric(df[col])
    temp = pd.DataFrame({"valor": values})
    temp = temp[temp["valor"].isin(LIKERT_LABELS.keys())].copy()

    if temp.empty:
        return pd.DataFrame(columns=["Respuesta", "Cantidad", "Porcentaje"])

    temp["Respuesta"] = temp["valor"].astype(int).map(LIKERT_LABELS)

    counts = (
        temp["Respuesta"]
        .value_counts()
        .reindex(LIKERT_ORDER)
        .fillna(0)
        .astype(int)
    )

    total = counts.sum()

    if total == 0:
        return pd.DataFrame(columns=["Respuesta", "Cantidad", "Porcentaje"])

    return pd.DataFrame(
        {
            "Respuesta": counts.index,
            "Cantidad": counts.values,
            "Porcentaje": (counts.values / total * 100).round(1),
        }
    )


def positive_count(df: pd.DataFrame, col: str) -> int:
    if df is None or df.empty or not col or col not in df.columns:
        return 0

    values = likert_to_numeric(df[col])
    return int(values.isin([4, 5]).sum())



def render_card_header(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="card-header-soft">
            <div class="section-title-card">{safe_text(title)}</div>
            <div class="section-subtitle-card">{safe_text(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )    


def render_note(text: str, color: str = "blue"):
    css_class = {
        "blue": "analysis-note-compact",
        "green": "analysis-note-compact-green",
        "yellow": "analysis-note-compact-yellow",
        "red": "analysis-note-compact-red",
    }.get(color, "analysis-note-compact")

    st.markdown(
        f"""
        <div class="{css_class}">
            {safe_text(text)}
        </div>
        """,
        unsafe_allow_html=True,
    )    


def horizontal_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    text_col: str = "Porcentaje",
    height: int = 315,
):
    if df.empty:
        return None

    plot_df = df.sort_values(x_col, ascending=True).copy()
    max_x = plot_df[x_col].max() if not plot_df.empty else 0
    x_range_max = max(max_x * 1.18, 1)

    fig = px.bar(
        plot_df,
        x=x_col,
        y=y_col,
        orientation="h",
        text=text_col,
        color=y_col,
        color_discrete_sequence=BASE_COLORS,
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
        margin=dict(l=5, r=72, t=5, b=10),
        xaxis=dict(
            title="",
            range=[0, x_range_max],
            showgrid=True,
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        yaxis=dict(title="", automargin=True),
        showlegend=False,
        font=dict(size=11),
    )

    return fig


def donut_chart(df: pd.DataFrame, names_col: str, values_col: str, height: int = 315):
    if df.empty:
        return None

    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        hole=0.52,
        color_discrete_sequence=BASE_COLORS,
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
        margin=dict(l=0, r=0, t=0, b=58),
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.10,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    )

    return fig


def make_stacked_likert_bar(values: pd.DataFrame, title_y: str, height: int = 110):
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
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        font=dict(size=11),
    )

    return fig
