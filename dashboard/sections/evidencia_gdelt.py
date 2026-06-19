import re
import textwrap
from collections import Counter

import pandas as pd
import streamlit as st
import plotly.express as px

from dashboard.components import topbar

from dashboard.data_loader import (
    load_triangulation_matrix,
    load_recommendation_rules,
)

import html

def html_block(content: str):
    compact_html = " ".join(
        line.strip()
        for line in textwrap.dedent(content).strip().splitlines()
        if line.strip()
    )
    st.markdown(compact_html, unsafe_allow_html=True)


def empty_state(message: str):
    html_block(
        f"""
        <div class="empty-state">
            {message}
        </div>
        """
    )


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


def count_pct(df: pd.DataFrame, col: str, accepted_values: list[str]):
    if df is None or df.empty or not col or col not in df.columns:
        return 0, 0.0

    values = df[col].fillna("").astype(str).str.strip()
    total = len(df)

    n = values.isin(accepted_values).sum()
    pct = round(n / total * 100, 1) if total else 0.0

    return int(n), pct


def distribution(df: pd.DataFrame, col: str, order: list[str] | None = None):
    if df is None or df.empty or not col or col not in df.columns:
        return []

    values = df[col].fillna("No registrado").astype(str).str.strip()
    counts = values.value_counts()

    if order:
        counts = counts.reindex(order).dropna().astype(int)

    total = counts.sum()

    if total == 0:
        return []

    return [
        {
            "label": str(label),
            "n": int(n),
            "pct": round(n / total * 100, 1),
        }
        for label, n in counts.items()
    ]


def _ed_esc(value) -> str:
    if value is None or pd.isna(value):
        return ""
    return html.escape(str(value))


def _level_class(level: str) -> str:
    text = str(level).lower()

    if "fuerte" in text:
        return "strong"
    if "media" in text:
        return "medium"
    if "contextual" in text or "normativa" in text:
        return "contextual"
    return "exploratory"


def render_triangulation_cards(matrix_df: pd.DataFrame) -> None:
    if matrix_df is None or matrix_df.empty:
        empty_state("No hay dimensiones disponibles con los filtros seleccionados.")
        return

    cards_html = ""

    for _, row in matrix_df.iterrows():
        dimension = _ed_esc(row.get("Dimensión", "Dimensión no disponible"))
        level = _ed_esc(row.get("Nivel", "Exploratoria"))
        lectura = _ed_esc(row.get("Lectura para tesis", "Lectura no disponible"))
        level_class = _level_class(level)

        cards_html += f"""
        <div class="ed-tri-card">
            <div class="ed-tri-card-head">
                <div class="ed-tri-dimension">{dimension}</div>
                <span class="ed-tri-badge {level_class}">{level}</span>
            </div>
            <div class="ed-tri-reading">{lectura}</div>
        </div>
        """

    html_block(
        f"""
        <div class="ed-tri-grid">
            {cards_html}
        </div>
        """
    )
def compact_triangulation_level(value: str) -> str:
    text = str(value).lower()

    if "fuerte" in text:
        return "Fuerte"
    if "media" in text:
        return "Media"
    if "normativa" in text or "contextual" in text:
        return "Contextual"
    if "exploratoria" in text:
        return "Exploratoria"

    return "Exploratoria"

def render_bars(
    items: list[dict],
    color_class: str = "",
    scale_to_max: bool = False,
):
    if not items:
        empty_state("No se encontraron datos suficientes para construir este indicador.")
        return

    max_pct = max(float(item.get("pct", 0) or 0) for item in items) or 1
    html = ""

    for item in items:
        pct = float(item.get("pct", 0) or 0)

        if scale_to_max:
            width = pct / max_pct * 100
        else:
            width = pct

        width = max(0, min(width, 100))
        fill_class = item.get("color_class", color_class)

        html += f"""
        <div class="ed-bar-row">
            <div class="ed-bar-head">
                <span>{item["label"]}</span>
                <span>{item["n"]} · {pct:.1f}%</span>
            </div>
            <div class="ed-track">
                <div class="ed-fill {fill_class}" style="width:{width:.1f}%;"></div>
            </div>
        </div>
        """

    html_block(html)


def social_platform_sentiment_summary(gdelt_df: pd.DataFrame):
    if gdelt_df is None or gdelt_df.empty:
        return pd.DataFrame(columns=["plataforma", "sentimiento", "registros"])

    if "case_id" not in gdelt_df.columns:
        return pd.DataFrame(columns=["plataforma", "sentimiento", "registros"])

    social_df = gdelt_df[gdelt_df["case_id"].astype(str).str.contains("social", case=False, na=False)].copy()

    if social_df.empty or "platform" not in social_df.columns or "sentiment_label" not in social_df.columns:
        return pd.DataFrame(columns=["plataforma", "sentimiento", "registros"])

    social_df = social_df[["platform", "sentiment_label"]].copy()
    social_df["plataforma"] = social_df["platform"].fillna("No registrado").astype(str).str.strip().str.title()
    social_df["sentimiento"] = (
        social_df["sentiment_label"]
        .fillna("neutral")
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"positivo": "Positivo", "positive": "Positivo", "pos": "Positivo",
                  "neutral": "Neutral", "neu": "Neutral", "negativo": "Negativo",
                  "negative": "Negativo", "neg": "Negativo"})
    )

    summary = (
        social_df.groupby(["plataforma", "sentimiento"], sort=False)
        .size()
        .reset_index(name="registros")
    )

    return summary


def render_platform_sentiment_chart(gdelt_df: pd.DataFrame):
    summary = social_platform_sentiment_summary(gdelt_df)

    if summary.empty:
        empty_state("No se encontraron registros sociales con columna de plataforma y sentimiento para esta visualización.")
        return

    fig = px.bar(
        summary,
        x="plataforma",
        y="registros",
        color="sentimiento",
        barmode="group",
        color_discrete_map={
            "Positivo": "#2ecc71",
            "Neutral": "#f4b942",
            "Negativo": "#ef6b6b",
        },
        category_orders={"sentimiento": ["Positivo", "Neutral", "Negativo"]},
        labels={"plataforma": "Plataforma", "registros": "Registros", "sentimiento": "Sentimiento"},
    )


    fig.update_layout(
        height=295,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=45, r=16, t=18, b=42),
        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="Registros", gridcolor="#e5e7eb"),
        font=dict(size=11),
    )

    fig.update_traces(hovertemplate="<b>%{x}</b><br>Sentimiento: %{fullData.name}<br>Registros: %{y}<extra></extra>")

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def gdelt_date_column(gdelt_df: pd.DataFrame):
    return find_first_existing_column(
        gdelt_df,
        [
            "date",
            "fecha",
            "day",
            "SQLDATE",
            "DATEADDED",
            "datetime",
            "timestamp",
            "eventdate",
        ],
    )


def gdelt_tone_column(gdelt_df: pd.DataFrame):
    return find_first_existing_column(
        gdelt_df,
        [
            "tone",
            "avg tone",
            "avgtone",
            "AvgTone",
            "sentiment",
            "tono",
            "GoldsteinScale",
        ],
    )


def gdelt_source_column(gdelt_df: pd.DataFrame):
    return find_first_existing_column(
        gdelt_df,
        [
            "source",
            "sourceurl",
            "sourcecommonname",
            "domain",
            "medio",
            "fuente",
            "url",
        ],
    )


def gdelt_text_column(gdelt_df: pd.DataFrame):
    return find_first_existing_column(
        gdelt_df,
        [
            "title",
            "titulo",
            "headline",
            "text",
            "content",
            "summary",
            "translation",
            "V2Themes",
            "themes",
        ],
    )


def prepare_gdelt_timeline(gdelt_df: pd.DataFrame):
    if gdelt_df is None or gdelt_df.empty:
        return pd.DataFrame(columns=["Fecha", "Registros"])

    date_col = gdelt_date_column(gdelt_df)

    if not date_col:
        return pd.DataFrame(columns=["Fecha", "Registros"])

    temp = gdelt_df[[date_col]].copy()

    temp["Fecha"] = pd.to_datetime(temp[date_col], errors="coerce")

    if temp["Fecha"].isna().all():
        temp["Fecha"] = pd.to_datetime(temp[date_col].astype(str).str[:8], format="%Y%m%d", errors="coerce")

    temp = temp.dropna(subset=["Fecha"])

    if temp.empty:
        return pd.DataFrame(columns=["Fecha", "Registros"])

    timeline = (
        temp.assign(Fecha=temp["Fecha"].dt.date)
        .groupby("Fecha")
        .size()
        .reset_index(name="Registros")
    )

    return timeline


def sentiment_label_column(df: pd.DataFrame):
    return find_first_existing_column(
        df,
        ["sentiment_label", "sentiment_raw_label", "label", "tone_label"],
    )


def sentiment_score_column(df: pd.DataFrame):
    return find_first_existing_column(
        df,
        ["sentiment_score", "sentiment_raw_score", "score", "avg_tone", "tone"],
    )


def gdelt_tone_summary(gdelt_df: pd.DataFrame):
    if gdelt_df is None or gdelt_df.empty:
        return None

    label_col = sentiment_label_column(gdelt_df)
    score_col = sentiment_score_column(gdelt_df)

    if label_col:
        labels = gdelt_df[label_col].fillna("").astype(str).str.strip().str.lower()
        counts = labels.value_counts()
        neg = int(counts.get("negativo", 0) + counts.get("negative", 0) + counts.get("neg", 0))
        neu = int(counts.get("neutral", 0) + counts.get("neu", 0))
        pos = int(counts.get("positivo", 0) + counts.get("positive", 0) + counts.get("pos", 0))
        total = int(counts.sum())
        mean = None
    else:
        neg = neu = pos = 0
        total = 0
        mean = None

    if score_col:
        tone = pd.to_numeric(gdelt_df[score_col], errors="coerce").dropna()
        if not tone.empty:
            mean = round(float(tone.mean()), 3)
            if total == 0:
                total = int(tone.count())
                neg = int((tone < 0).sum())
                neu = int((tone == 0).sum())
                pos = int((tone > 0).sum())
    else:
        tone = pd.Series(dtype=float)

    if total == 0:
        return None

    return {
        "mean": mean,
        "min": round(float(tone.min()), 3) if not tone.empty else None,
        "max": round(float(tone.max()), 3) if not tone.empty else None,
        "neg": int(neg),
        "neu": int(neu),
        "pos": int(pos),
        "total": int(total),
    }


def gdelt_top_sources(gdelt_df: pd.DataFrame, limit: int = 8):
    if gdelt_df is None or gdelt_df.empty:
        return []

    source_col = gdelt_source_column(gdelt_df)

    if not source_col:
        return []

    counts = (
        gdelt_df[source_col]
        .fillna("No registrado")
        .astype(str)
        .str.strip()
        .replace("", "No registrado")
        .value_counts()
        .head(limit)
    )

    total = counts.sum()

    return [
        {
            "label": str(label)[:55],
            "n": int(n),
            "pct": round(n / total * 100, 1) if total else 0.0,
        }
        for label, n in counts.items()
    ]


def gdelt_keywords(gdelt_df: pd.DataFrame, limit: int = 10):
    if gdelt_df is None or gdelt_df.empty:
        return []

    text_col = gdelt_text_column(gdelt_df)

    if not text_col:
        return []

    stopwords = {
        "que", "para", "con", "por", "una", "del", "los", "las", "and", "the",
        "de", "la", "el", "en", "a", "y", "o", "un", "al", "se", "su", "es",
        "lo", "como", "más", "pero", "sus", "sin", "sobre", "from", "this",
        "that", "are", "was", "were", "not", "have", "has", "political",
    }

    text = " ".join(gdelt_df[text_col].fillna("").astype(str).tolist()).lower()
    words = re.findall(r"[a-záéíóúñü]{4,}", text)

    filtered = [w for w in words if w not in stopwords]
    counts = Counter(filtered).most_common(limit)

    total = sum(n for _, n in counts)

    return [
        {
            "label": word,
            "n": int(n),
            "pct": round(n / total * 100, 1) if total else 0.0,
        }
        for word, n in counts
    ]


def render_gdelt_timeline(gdelt_df: pd.DataFrame):
    timeline = prepare_gdelt_timeline(gdelt_df)

    if timeline.empty:
        empty_state("No se encontró una columna temporal válida en la base GDELT.")
        return

    fig = px.line(
        timeline,
        x="Fecha",
        y="Registros",
        markers=True,
    )

    fig.update_layout(
        height=260,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=0, r=10, t=10, b=30),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="Registros", gridcolor="#e5e7eb"),
        font=dict(size=11),
    )

    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Registros: %{y}<extra></extra>",
        line=dict(width=3),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})




def render_tone_card(gdelt_df: pd.DataFrame):
    tone = gdelt_tone_summary(gdelt_df)

    if not tone:
        empty_state("No se encontró una columna de sentimiento/tono válida en la base social o de noticias.")
        return

    total = tone["total"] or 1

    items = [
        {
            "label": "Tono positivo",
            "n": tone["pos"],
            "pct": round(tone["pos"] / total * 100, 1),
            "color_class": "green",
        },
        {
            "label": "Tono neutro",
            "n": tone["neu"],
            "pct": round(tone["neu"] / total * 100, 1),
            "color_class": "yellow",
        },
        {
            "label": "Tono negativo",
            "n": tone["neg"],
            "pct": round(tone["neg"] / total * 100, 1),
            "color_class": "red",
        },
    ]

    html_block(
        f"""
        <div class="ed-tone-grid">
            <div class="ed-tone-card blue">
                <div class="ed-tone-title">Score medio de sentimiento</div>
                <div class="ed-tone-value">{tone['mean'] if tone['mean'] is not None else 'N/D'}</div>
                <div class="ed-tone-text">Promedio del puntaje disponible en registros válidos.</div>
            </div>

            <div class="ed-tone-card green">
                <div class="ed-tone-title">Rango observado</div>
                <div class="ed-tone-value">{tone["min"]} / {tone["max"]}</div>
                <div class="ed-tone-text">Valor mínimo y máximo registrado en el corpus digital.</div>
            </div>

            <div class="ed-tone-card yellow">
                <div class="ed-tone-title">Registros clasificados</div>
                <div class="ed-tone-value">{tone['total']:,}</div>
                <div class="ed-tone-text">Casos usados para el resumen de sentimiento.</div>
            </div>
        </div>
        """
    )

    render_bars(items)

def render_source_method_card(n_survey: int, n_gdelt: int):
    html_block(
        f"""
        <div class="ed-source-grid">
            <div class="ed-source-card blue">
                <div class="ed-source-title">Encuesta</div>
                <div class="ed-source-text">
                    Evidencia perceptual/autodeclarada. Permite observar cómo la ciudadanía experimentó
                    exposición digital, automatización, contenido manipulado y verificación informativa.
                    <br><br><strong>n = {n_survey:,} respuestas</strong>
                </div>
            </div>

            <div class="ed-source-card green">
                <div class="ed-source-title">Redes y medios</div>
                <div class="ed-source-text">
                    Evidencia textual de redes y medios. Permite observar volumen, evolución temporal,
                    fuentes y sentimiento asociado al ecosistema electoral digital.
                    <br><br><strong>n = {n_gdelt:,} registros</strong>
                </div>
            </div>

            <div class="ed-source-card yellow">
                <div class="ed-source-title">Triangulación</div>
                <div class="ed-source-text">
                    Cruce interpretativo entre percepción ciudadana y señales externas de cobertura.
                    No prueba causalidad, pero fortalece la lectura contextual del fenómeno estudiado.
                </div>
            </div>
        </div>
        """
    )


def render_method_fact_sheet(n_survey: int, n_digital: int):
    html_block(
        f"""
        <div class="ed-fact-grid">
            <div class="ed-fact-item">
                <div class="ed-fact-label">Periodo analizado</div>
                <div class="ed-fact-value">Febrero – mayo de 2025</div>
            </div>

            <div class="ed-fact-item">
                <div class="ed-fact-label">Fuente primaria</div>
                <div class="ed-fact-value">Encuesta aplicada a participantes de la comunidad UCE</div>
            </div>

            <div class="ed-fact-item">
                <div class="ed-fact-label">Fuente secundaria</div>
                <div class="ed-fact-value">Registros digitales provenientes de GDELT, medios digitales y redes sociales procesadas</div>
            </div>

            <div class="ed-fact-item">
                <div class="ed-fact-label">Unidad de análisis digital</div>
                <div class="ed-fact-value">Texto, título o contenido publicado en medios y plataformas digitales</div>
            </div>

            <div class="ed-fact-item">
                <div class="ed-fact-label">Técnicas aplicadas</div>
                <div class="ed-fact-value">Limpieza textual, frecuencia de términos, análisis de sentimiento y agrupación por fuente/plataforma</div>
            </div>

            <div class="ed-fact-item">
                <div class="ed-fact-label">Alcance</div>
                <div class="ed-fact-value">Análisis contextual e interpretativo, sin inferencia causal directa</div>
            </div>

            <div class="ed-fact-item">
                <div class="ed-fact-label">Tamaño de encuesta</div>
                <div class="ed-fact-value">n = {n_survey:,} respuestas</div>
            </div>

            <div class="ed-fact-item">
                <div class="ed-fact-label">Corpus digital</div>
                <div class="ed-fact-value">n = {n_digital:,} registros procesados</div>
            </div>
        </div>
        """
    )

def render_evidencia_digital(
    survey_df: pd.DataFrame,
    gdelt_df: pd.DataFrame | None = None,
    metrics_df: pd.DataFrame | None = None,
):
    n_survey = len(survey_df) if survey_df is not None and not survey_df.empty else 0
    n_digital = len(gdelt_df) if gdelt_df is not None and not gdelt_df.empty else 0

    topbar(
        title="Evidencia Digital y Triangulación",
        subtitle=(
            "Contraste interpretativo entre resultados de encuesta, registros digitales externos "
            "y patrones exploratorios del modelado."
        ),
        pill_text=f"Encuesta n={n_survey:,} · Evidencia digital n={n_digital:,}",
    )

    html_block(
        """
        <div class="ed-note-yellow" style="margin-bottom: 1.2rem;">
            <strong>Nota metodológica:</strong> Este módulo integra resultados de encuesta con evidencia digital externa.
            La evidencia digital puede incluir registros GDELT, medios digitales y redes sociales procesadas. La triangulación
            permite contrastar patrones de percepción ciudadana con señales del ecosistema informativo digital.
        </div>
        """
    )

    if survey_df is None or survey_df.empty:
        empty_state("No se encontraron datos de encuesta para construir esta sección.")
        return

    # =====================================================
    # 1. Detección de columnas
    # =====================================================
    exposicion_col = find_first_existing_column(
        survey_df,
        [
            "Durante la campaña presidencial entre Luisa González y Daniel Noboa, ¿con qué frecuencia vio o recibió contenido político en redes sociales o plataformas digitales?",
            "frecuencia vio o recibió contenido político",
            "contenido político en redes sociales",
        ],
    )

    automatizacion_col = find_first_existing_column(
        survey_df,
        [
            "percibe_automatizacion",
            "automatizacion",
            "automatización",
        ],
    )

    falso_col = find_first_existing_column(
        survey_df,
        [
            '¿Vio alguna vez un video, imagen, audio o noticia política de la campaña entre Luisa González y Daniel Noboa que le pareció "falso", "manipulado" o generado con IA?',
            "falso",
            "manipulado",
            "generado con IA",
        ],
    )

    verificacion_col = find_first_existing_column(
        survey_df,
        [
            "¿Realiza alguna verificación (chequea fuentes, busca noticias, consulta otras personas) de la información política digital antes de compartirla?",
            "verificación",
            "chequea fuentes",
            "antes de compartirla",
        ],
    )

    # =====================================================
    # 2. KPI superiores
    # =====================================================
    _, exposicion_diaria_pct = count_pct(
        survey_df,
        exposicion_col,
        ["Varias veces al día", "Una vez al día"],
    )

    _, falso_pct = count_pct(
        survey_df,
        falso_col,
        ["Sí, algunas veces", "Sí, muchas veces"],
    )

    _, automatizacion_pct = count_pct(
        survey_df,
        automatizacion_col,
        ["Sí, lo he notado claramente"],
    )

    _, verificacion_pct = count_pct(
        survey_df,
        verificacion_col,
        ["Siempre", "A veces"],
    )

    tone = gdelt_tone_summary(gdelt_df)
    tone_value = f"{tone['mean']:.3f}" if tone else "N/D"

    html_block(
        f"""
        <div class="ed-kpi-grid">
            <div class="ed-kpi blue">
                <div class="ed-kpi-label">Encuesta · exposición diaria</div>
                <div class="ed-kpi-value">{exposicion_diaria_pct:.1f}%</div>
                <div class="ed-kpi-help">Participantes que reportan contacto frecuente con contenido político digital.</div>
            </div>

            <div class="ed-kpi red">
                <div class="ed-kpi-label">Encuesta · contenido sospechoso percibido</div>
                <div class="ed-kpi-value">{falso_pct:.1f}%</div>
                <div class="ed-kpi-help">Participantes que percibieron contenido falso, manipulado o generado con IA.</div>
            </div>

            <div class="ed-kpi green">
                <div class="ed-kpi-label">Evidencia digital · registros</div>
                <div class="ed-kpi-value">{n_digital:,}</div>
                <div class="ed-kpi-help">Registros de GDELT, medios digitales o redes sociales disponibles para análisis.</div>
            </div>

            <div class="ed-kpi yellow">
                <div class="ed-kpi-label">Evidencia digital · tono promedio</div>
                <div class="ed-kpi-value">{tone_value}</div>
                <div class="ed-kpi-help">Promedio de tono o sentimiento en registros digitales válidos.</div>
            </div>
        </div>
        """
    )

    # =====================================================
    # 3. Tabs principales
    # =====================================================
    tab_encuesta, tab_digital, tab_interpretacion, tab_matriz, tab_diseno = st.tabs(
        [
            "Datos de encuesta",
            "Evidencia digital",
            "Triangulación e interpretación",
            "Matriz técnica y recomendaciones",
            "Alcance metodológico",
        ]
    )

    # =====================================================
    # TAB 1: DISEÑO METODOLÓGICO
    # =====================================================
    with tab_diseno:
        with st.container(border=True, key="card_ed_fuentes"):
            html_block(
                """
                <div class="section-title-card">Diseño de triangulación digital</div>
                <div class="section-subtitle-card">
                    Integración de fuente primaria mediante encuesta y fuente secundaria mediante evidencia digital externa.
                </div>
                """
            )
            render_source_method_card(n_survey, n_digital)

        st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)

        with st.container(border=True, key="card_ed_alcance"):
            html_block(
                """
                <div class="section-title-card">Alcance del módulo</div>
                <div class="section-subtitle-card">
                    Este apartado no reemplaza el modelo predictivo. Su propósito es contextualizar la percepción ciudadana
                    con señales externas del ecosistema digital electoral.
                </div>

                <div class="ed-source-grid">
                    <div class="ed-source-card blue">
                        <div class="ed-source-title">Encuesta</div>
                        <div class="ed-source-text">
                            Mide percepción, exposición, reconocimiento de automatización, contenido manipulado y prácticas de verificación.
                        </div>
                    </div>

                    <div class="ed-source-card green">
                        <div class="ed-source-title">GDELT y medios digitales</div>
                        <div class="ed-source-text">
                            Permiten observar cobertura, fuentes, términos recurrentes, temporalidad y sentimiento del entorno informativo.
                        </div>
                    </div>

                    <div class="ed-source-card yellow">
                        <div class="ed-source-title">Redes sociales</div>
                        <div class="ed-source-text">
                            Cuando existen registros sociales procesados, permiten comparar sentimiento por plataforma y señales de interacción digital.
                        </div>
                    </div>
                </div>
                """
            )

        st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)


        with st.expander("Ver ficha técnica metodológica", expanded=False):
            st.markdown(
                """
                **Periodo analizado:** febrero–mayo de 2025.  
                **Fuente primaria:** encuesta aplicada a participantes de la comunidad UCE.  
                **Fuente secundaria:** registros digitales provenientes de GDELT, medios digitales y redes sociales procesadas.  
                **Técnicas aplicadas:** limpieza textual, frecuencia de términos, análisis de sentimiento y agrupación por fuente/plataforma.  
                **Alcance:** análisis contextual e interpretativo, sin inferencia causal directa.
                """
            )     

    # =====================================================
    # TAB 2: DATOS DE ENCUESTA
    # =====================================================
    with tab_encuesta:
        col1, col2 = st.columns(2, gap="large")

        with col1:
            with st.container(border=True, key="card_ed_encuesta_exposicion"):
                html_block(
                    """
                    <div class="section-title-card">Encuesta · exposición política digital</div>
                    <div class="section-subtitle-card">
                        Frecuencia con la que los encuestados vieron o recibieron contenido político durante la campaña.
                    </div>
                    """
                )

                order = [
                    "Varias veces al día",
                    "Una vez al día",
                    "Varias veces a la semana",
                    "Rara vez",
                    "Nunca",
                ]
                render_bars(distribution(survey_df, exposicion_col, order), "blue")

                html_block(
                    """
                    <div class="ed-note-blue">
                        Este indicador describe el nivel de contacto ciudadano con el ecosistema político digital.
                    </div>
                    """
                )

        with col2:
            with st.container(border=True, key="card_ed_encuesta_falso"):
                html_block(
                    """
                    <div class="section-title-card">Encuesta · contenido percibido como falso, manipulado o generado con IA</div>
                    <div class="section-subtitle-card">
                        Frecuencia con la que los encuestados percibieron piezas políticas potencialmente falsas o manipuladas.
                    </div>
                    """
                )

                order = [
                    "Sí, muchas veces",
                    "Sí, algunas veces",
                    "No estoy seguro/a",
                    "No",
                ]
                render_bars(distribution(survey_df, falso_col, order), "red")

                html_block(
                    """
                    <div class="ed-note-red">
                        Este indicador aporta evidencia perceptual sobre desinformación, deepfakes y manipulación informativa.
                    </div>
                    """
                )

        st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2, gap="large")

        with col3:
            with st.container(border=True, key="card_ed_encuesta_automatizacion"):
                html_block(
                    """
                    <div class="section-title-card">Encuesta · automatización percibida</div>
                    <div class="section-subtitle-card">
                        Reconocimiento ciudadano de posibles patrones automatizados en el ecosistema digital electoral.
                    </div>
                    """
                )

                order = [
                    "Sí, lo he notado claramente",
                    "Tal vez, pero no estoy seguro/a",
                    "No",
                ]
                render_bars(distribution(survey_df, automatizacion_col, order), "yellow")

                html_block(
                    """
                    <div class="ed-note-yellow">
                        La automatización percibida funciona como señal ciudadana sobre bots, repetición coordinada o amplificación artificial.
                    </div>
                    """
                )

        with col4:
            with st.container(border=True, key="card_ed_encuesta_verificacion"):
                html_block(
                    """
                    <div class="section-title-card">Encuesta · verificación informativa</div>
                    <div class="section-subtitle-card">
                        Prácticas declaradas de chequeo de fuentes, búsqueda de noticias o consulta antes de compartir información política.
                    </div>
                    """
                )

                order = ["Siempre", "A veces", "Rara vez", "Nunca"]
                render_bars(distribution(survey_df, verificacion_col, order), "green")

                html_block(
                    """
                    <div class="ed-note-green">
                        La verificación informativa representa un componente de alfabetización mediática frente al contenido político digital.
                    </div>
                    """
                )

    # =====================================================
    # TAB 3: EVIDENCIA DIGITAL
    # =====================================================
    with tab_digital:
        col5, col6 = st.columns(2, gap="large")

        with col5:
            with st.container(border=True, key="card_ed_social_sentimiento"):
                html_block(
                    """
                    <div class="section-title-card">Redes sociales procesados · sentimiento por plataforma</div>
                    <div class="section-subtitle-card">
                        Distribución de tono positivo, neutro y negativo en los registros sociales disponibles por plataforma.
                    </div>
                    """
                )

                render_platform_sentiment_chart(gdelt_df)

                html_block(
                    """
                    <div class="ed-note-green">
                        Esta visualización se activa cuando existen registros sociales procesados con plataforma y sentimiento.
                    </div>
                    """
                )

        with col6:
            with st.container(border=True, key="card_ed_gdelt_tono"):
                html_block(
                    """
                    <div class="section-title-card">Evidencia digital · resumen de sentimiento</div>
                    <div class="section-subtitle-card">
                        Resumen del tono o sentimiento disponible en registros de GDELT, medios digitales o redes sociales.
                    </div>
                    """
                )

                if gdelt_df is not None and not gdelt_df.empty:
                    render_tone_card(gdelt_df)
                    html_block(
                        """
                        <div class="ed-note-yellow">
                            El tono digital permite contextualizar la orientación emocional o valorativa de los registros observados.
                        </div>
                        """
                    )
                else:
                    empty_state("No se ha cargado una base digital con columna de tono o sentimiento.")

        st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)

        col7, col8 = st.columns(2, gap="large")

        with col7:
            with st.container(border=True, key="card_ed_gdelt_fuentes"):
                html_block(
                    """
                    <div class="section-title-card">Evidencia digital · principales fuentes</div>
                    <div class="section-subtitle-card">
                        Fuentes, dominios, medios o plataformas con mayor presencia dentro del corpus digital.
                    </div>
                    """
                )

                if gdelt_df is not None and not gdelt_df.empty:
                    render_bars(gdelt_top_sources(gdelt_df), "blue")
                    html_block(
                        """
                        <div class="ed-note-blue">
                            La distribución de fuentes ayuda a identificar concentración o diversidad dentro del corpus externo.
                        </div>
                        """
                    )
                else:
                    empty_state("No se ha cargado una base digital con fuentes, dominios o URLs.")

        with col8:
            with st.container(border=True, key="card_ed_gdelt_keywords"):
                html_block(
                    """
                    <div class="section-title-card">Evidencia digital · términos recurrentes</div>
                    <div class="section-subtitle-card">
                        Palabras o temas frecuentes extraídos de texto, títulos, contenidos o resúmenes disponibles.
                    </div>
                    """
                )

                if gdelt_df is not None and not gdelt_df.empty:
                    render_bars(gdelt_keywords(gdelt_df), "green")
                    html_block(
                        """
                        <div class="ed-note-green">
                            Los términos recurrentes ayudan a describir los ejes temáticos dominantes en la evidencia digital.
                        </div>
                        """
                    )
                else:
                    empty_state("No se ha cargado una base digital con texto, títulos o contenidos.")

        st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)

        with st.container(border=True, key="card_ed_gdelt_evolucion"):
            html_block(
                """
                <div class="section-title-card">Evidencia digital · evolución temporal</div>
                <div class="section-subtitle-card">
                    Distribución temporal de registros digitales durante el periodo de análisis.
                </div>
                """
            )

            if gdelt_df is not None and not gdelt_df.empty:
                render_gdelt_timeline(gdelt_df)

            else:
                empty_state("No se ha cargado una base digital con fechas válidas.")

            html_block(
                """
                <div class="ed-note-blue">
                    La evolución temporal muestra variaciones en el volumen de registros digitales durante el periodo analizado.
                    Los picos de actividad no implican causalidad; únicamente indican mayor concentración de registros en fechas específicas.
                </div>
                """
            )    
    # =====================================================
    # TAB 4: TRIANGULACIÓN E INTERPRETACIÓN
    # =====================================================
    with tab_interpretacion:
        with st.container(border=True, key="card_ed_triangulacion"):
            html_block(
                """
                <div class="section-title-card">Triangulación entre encuesta y evidencia digital</div>
                <div class="section-subtitle-card">
                    Cruce interpretativo entre experiencia ciudadana declarada y señales digitales externas del ecosistema informativo.
                </div>
                """
            )

            digital_status = "disponible" if n_digital > 0 else "pendiente de carga"

            html_block(
                f"""
                <div class="ed-source-grid">
                    <div class="ed-source-card blue">
                        <div class="ed-source-title">Percepción ciudadana</div>
                        <div class="ed-source-text">
                            La encuesta muestra exposición diaria de <strong>{exposicion_diaria_pct:.1f}%</strong>,
                            percepción de contenido manipulado de <strong>{falso_pct:.1f}%</strong> y automatización clara de
                            <strong>{automatizacion_pct:.1f}%</strong>.
                        </div>
                    </div>

                    <div class="ed-source-card green">
                        <div class="ed-source-title">Señal digital externa</div>
                        <div class="ed-source-text">
                            El corpus digital está <strong>{digital_status}</strong> con <strong>{n_digital:,}</strong> registros.
                            Permite observar volumen, fuentes, sentimiento y evolución temporal de la cobertura digital.
                        </div>
                    </div>

                    <div class="ed-source-card yellow">
                        <div class="ed-source-title">Valor analítico</div>
                        <div class="ed-source-text">
                            La triangulación no prueba causalidad, pero fortalece la interpretación del vínculo entre circulación
                            digital de información, percepción de manipulación y confianza electoral.
                        </div>
                    </div>
                </div>
                """
            )

        st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)

        with st.container(border=True, key="card_ed_interpretacion"):
            html_block(
                """
                <div class="section-title-card">Lectura interpretativa</div>
                <div class="section-subtitle-card">
                    Síntesis visual de los indicadores principales del módulo.
                </div>
                """
            )

            html_block(
                f"""
                <div class="interpretation-grid">
                    <div class="interpretation-box blue">
                        <div class="interpretation-value">{exposicion_diaria_pct:.1f}%</div>
                        <div class="interpretation-label">
                            reportó exposición frecuente a contenido político digital.
                        </div>
                    </div>

                    <div class="interpretation-box red">
                        <div class="interpretation-value">{falso_pct:.1f}%</div>
                        <div class="interpretation-label">
                            percibió contenido político falso, manipulado o generado con IA.
                        </div>
                    </div>

                    <div class="interpretation-box green">
                        <div class="interpretation-value">{n_digital:,}</div>
                        <div class="interpretation-label">
                            registros digitales disponibles para contextualizar el ecosistema electoral.
                        </div>
                    </div>

                    <div class="interpretation-box yellow">
                        <div class="interpretation-value">{tone_value}</div>
                        <div class="interpretation-label">
                            tono promedio observado en registros digitales válidos.
                        </div>
                    </div>
                </div>

                <div class="ed-note-green">
                    En conjunto, la encuesta y la evidencia digital permiten diferenciar entre percepción ciudadana y señal externa.
                    La encuesta muestra experiencia declarada; la evidencia digital aporta contexto sobre medios, redes, fuentes,
                    términos, sentimiento y temporalidad. La lectura es complementaria y no implica causalidad directa.
                </div>
                """
            )

        st.caption(
            "Nota metodológica: esta pestaña triangula evidencia autodeclarada de encuesta con evidencia digital externa "
            "proveniente de GDELT, medios digitales y redes sociales cuando estas se encuentran disponibles. "
            "La triangulación es interpretativa y no establece causalidad directa."
        )

    # =====================================================
    # TAB 5: MATRIZ TÉCNICA Y RECOMENDACIONES
    # =====================================================
    with tab_matriz:
        triangulation_df = load_triangulation_matrix()
        recommendation_rules = load_recommendation_rules()

        if triangulation_df.empty:
            empty_state(
                "No se encontró la matriz técnica de triangulación. "
                "Verifica el archivo triangulation_matrix.csv en outputs/latest/tables."
            )
        else:
            html_block(
                """
                <div class="ed-note-blue" style="margin-bottom: 1rem;">
                    <strong>Lectura metodológica:</strong> esta matriz resume cómo se conectan los hallazgos
                    de encuesta, evidencia digital contextual y patrones del modelado exploratorio.
                    No representa causalidad ni generalización poblacional.
                </div>
                """
            )

            matrix_df = triangulation_df.copy()

            if "Nivel de triangulación" in matrix_df.columns:
                matrix_df["Nivel"] = matrix_df["Nivel de triangulación"].apply(compact_triangulation_level)
            else:
                matrix_df["Nivel"] = "Exploratoria"

            levels = ["Todos"] + matrix_df["Nivel"].dropna().astype(str).unique().tolist()

            c1, c2 = st.columns([0.8, 1.2], gap="medium")

            with c1:
                selected_level = st.selectbox(
                    "Nivel de triangulación",
                    levels,
                    key="ed_tri_level_filter",
                )

            with c2:
                search_text = st.text_input(
                    "Buscar dimensión o lectura",
                    placeholder="Ejemplo: bots, deepfakes, regulación...",
                    key="ed_tri_search",
                )

            filtered_matrix_df = matrix_df.copy()

            if selected_level != "Todos":
                filtered_matrix_df = filtered_matrix_df[
                    filtered_matrix_df["Nivel"].astype(str) == selected_level
                ]

            if search_text.strip():
                query = search_text.lower().strip()
                filtered_matrix_df = filtered_matrix_df[
                    filtered_matrix_df.apply(
                        lambda row: query in " ".join(row.astype(str)).lower(),
                        axis=1,
                    )
                ]

            compact_cols = [
                "Dimensión",
                "Nivel",
                "Lectura para tesis",
            ]

            compact_cols = [
                col for col in compact_cols
                if col in filtered_matrix_df.columns
            ]

            with st.container(border=True, key="card_ed_matriz_tecnica"):
                html_block(
                    """
                    <div class="section-title-card">Matriz técnica de triangulación</div>
                    <div class="section-subtitle-card">
                        Vista integrada de dimensiones analíticas, nivel de triangulación y lectura para tesis.
                    </div>
                    """
                )


                render_triangulation_cards(filtered_matrix_df[compact_cols])

                with st.expander("Ver matriz técnica completa"):
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
                    key="download_ed_triangulation_matrix",
                )

            st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)

            with st.container(border=True, key="card_ed_recomendaciones"):
                html_block(
                    """
                    <div class="section-title-card">Recomendaciones derivadas</div>
                    <div class="section-subtitle-card">
                        Acciones técnicas, institucionales o académicas vinculadas con los hallazgos integrados.
                    </div>
                    """
                )

                if recommendation_rules.empty:
                    empty_state("No se encontraron reglas de recomendación.")
                else:
                    rec_cols = st.columns(2, gap="medium")

                    for idx, row in recommendation_rules.reset_index(drop=True).iterrows():
                        with rec_cols[idx % 2]:
                            with st.container(border=True, key=f"card_ed_rec_{idx}"):
                                html_block(
                                    f"""
                                    <div class="section-title-card" style="font-size:1rem;">
                                        {row.get("Condición analítica", "Condición no disponible")}
                                    </div>
                                    <div class="section-subtitle-card">
                                        Tipo: {row.get("Tipo", "No definido")} · Actor: {row.get("Actor sugerido", "No definido")}
                                    </div>
                                    <div class="ed-note-blue">
                                        {row.get("Recomendación técnica", "Recomendación no disponible")}
                                    </div>
                                    """
                                )

                    csv_rec = recommendation_rules.to_csv(index=False, encoding="utf-8-sig")

                    st.download_button(
                        "Descargar reglas de recomendación",
                        data=csv_rec,
                        file_name="recommendation_rules.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="download_ed_recommendation_rules",
                    )
