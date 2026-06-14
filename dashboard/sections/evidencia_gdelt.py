import re
import textwrap
from collections import Counter

import pandas as pd
import streamlit as st
import plotly.express as px

from dashboard.components import topbar


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


def render_bars(items: list[dict], color_class: str = ""):
    if not items:
        empty_state("No se encontraron datos suficientes para construir este indicador.")
        return

    max_pct = max(item["pct"] for item in items) or 1
    html = ""

    for item in items:
        width = item["pct"] / max_pct * 100

        html += f"""
        <div class="ed-bar-row">
            <div class="ed-bar-head">
                <span>{item["label"]}</span>
                <span>{item["n"]} · {item["pct"]:.1f}%</span>
            </div>
            <div class="ed-track">
                <div class="ed-fill {color_class}" style="width:{width:.1f}%;"></div>
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
        height=320,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=0, r=10, t=10, b=30),
        legend=dict(title="Sentimiento"),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="Registros", gridcolor="#e5e7eb"),
        font=dict(size=11),
    )

    fig.update_traces(hovertemplate="<b>%{x}</b><br>Sentimiento: %{fullData.name}<br>Registros: %{y}<extra></extra>")

    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


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

    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def render_tone_card(gdelt_df: pd.DataFrame):
    tone = gdelt_tone_summary(gdelt_df)

    if not tone:
        empty_state("No se encontró una columna de sentimiento/tono válida en la base social o de noticias.")
        return

    items = [
        {"label": "Tono positivo", "n": tone["pos"], "pct": round(tone["pos"] / tone["total"] * 100, 1)},
        {"label": "Tono neutro", "n": tone["neu"], "pct": round(tone["neu"] / tone["total"] * 100, 1)},
        {"label": "Tono negativo", "n": tone["neg"], "pct": round(tone["neg"] / tone["total"] * 100, 1)},
    ]

    html_block(
        f"""
        <div class="ed-source-grid">
            <div class="ed-source-card blue">
                <div class="ed-source-title">Score medio de sentimiento</div>
                <div class="ed-kpi-value">{tone['mean'] if tone['mean'] is not None else 'N/D'}</div>
                <div class="ed-source-text">Promedio de sentimiento en registros de redes o noticias válidos.</div>
            </div>
            <div class="ed-source-card green">
                <div class="ed-source-title">Rango observado</div>
                <div class="ed-kpi-value">{tone["min"]} / {tone["max"]}</div>
                <div class="ed-source-text">Valor mínimo y máximo de tono registrado.</div>
            </div>
            <div class="ed-source-card yellow">
                <div class="ed-source-title">Registros con sentimiento</div>
                <div class="ed-kpi-value">{tone['total']}</div>
                <div class="ed-source-text">Casos de texto social o periodístico usados para el resumen de sentimiento.</div>
            </div>
        </div>
        """
    )

    render_bars(items, "yellow")


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


def render_evidencia_digital(
    survey_df: pd.DataFrame,
    gdelt_df: pd.DataFrame | None = None,
):
    n_survey = len(survey_df) if survey_df is not None and not survey_df.empty else 0
    n_gdelt = len(gdelt_df) if gdelt_df is not None and not gdelt_df.empty else 0

    topbar(
        title="Sentimiento social + Encuesta",
        subtitle=(
            "Triangulación entre evidencia autodeclarada de la encuesta y señales digitales de redes/medios "
            "sobre exposición, automatización, contenido manipulado, cobertura y sentimiento digital."
        ),
        pill_text=f"n = {n_survey:,} encuestas · GDELT = {n_gdelt:,} registros",
    )

    if survey_df is None or survey_df.empty:
        empty_state("No se encontraron datos de encuesta para construir esta sección.")
        return

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
            "¿Vio alguna vez un video, imagen, audio o noticia política de la campaña entre Luisa González y Daniel Noboa que le pareció “falso”, “manipulado” o generado con IA?",
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

    interaccion_col = find_first_existing_column(
        survey_df,
        [
            "¿Qué tipo de interacción tuvo con el contenido político digital relacionado a la campaña Noboa vs. González?",
            "tipo de interacción",
            "interacción tuvo con el contenido político digital",
        ],
    )

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
                <div class="ed-kpi-help">vio contenido político digital al menos una vez al día.</div>
            </div>

            <div class="ed-kpi red">
                <div class="ed-kpi-label">Encuesta · contenido manipulado</div>
                <div class="ed-kpi-value">{falso_pct:.1f}%</div>
                <div class="ed-kpi-help">percibió contenido falso, manipulado o generado con IA.</div>
            </div>

            <div class="ed-kpi green">
                <div class="ed-kpi-label">Redes/medios · registros digitales</div>
                <div class="ed-kpi-value">{n_gdelt:,}</div>
                <div class="ed-kpi-help">registros externos disponibles para análisis documental.</div>
            </div>

            <div class="ed-kpi yellow">
                <div class="ed-kpi-label">Redes/medios · tono promedio</div>
                <div class="ed-kpi-value">{tone_value}</div>
                <div class="ed-kpi-help">promedio de tono en registros GDELT válidos.</div>
            </div>
        </div>
        """
    )

    with st.container(border=True, key="card_ed_fuentes"):
        html_block(
            """
            <div class="section-title-card">Diseño de triangulación digital</div>
            <div class="section-subtitle-card">
                La pestaña integra dos tipos de evidencia: percepción ciudadana mediante encuesta y señales externas de cobertura digital mediante redes y medios.
            </div>
            """
        )
        render_source_method_card(n_survey, n_gdelt)

    st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True, key="card_ed_encuesta_exposicion"):
            html_block(
                """
                <div class="section-title-card">Encuesta · exposición política digital</div>
                <div class="section-subtitle-card">
                    Frecuencia con la que los encuestados vieron o recibieron contenido político durante la campaña Noboa vs. González.
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
                    Este indicador muestra el nivel de contacto ciudadano con el ecosistema político digital durante la campaña.
                </div>
                """
            )

    with col2:
        with st.container(border=True, key="card_ed_encuesta_falso"):
            html_block(
                """
                <div class="section-title-card">Encuesta · contenido falso, manipulado o generado con IA</div>
                <div class="section-subtitle-card">
                    Frecuencia con la que los encuestados percibieron piezas políticas potencialmente falsas, manipuladas o generadas con IA.
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
                    La percepción de contenido manipulado refuerza la preocupación por deepfakes, desinformación y confianza informativa.
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
                    La automatización percibida funciona como evidencia ciudadana sobre bots, comportamiento coordinado o repetición artificial de mensajes.
                </div>
                """
            )

    with col4:
        with st.container(border=True, key="card_ed_encuesta_verificacion"):
            html_block(
                """
                <div class="section-title-card">Encuesta · verificación informativa</div>
                <div class="section-subtitle-card">
                    Prácticas declaradas de chequeo de fuentes, búsqueda de noticias o consulta a otras personas antes de compartir información política.
                </div>
                """
            )

            order = ["Siempre", "A veces", "Rara vez", "Nunca"]
            render_bars(distribution(survey_df, verificacion_col, order), "green")

            html_block(
                """
                <div class="ed-note-green">
                    La verificación informativa representa un componente de alfabetización mediática frente a la circulación de contenido político digital.
                </div>
                """
            )

    st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)

    col5, col6 = st.columns(2, gap="large")

    with col5:
        with st.container(border=True, key="card_ed_gdelt_timeline"):
            html_block(
                """
                <div class="section-title-card">Redes sociales · sentimiento por plataforma</div>
                <div class="section-subtitle-card">
                    Distribución de tono positivo, neutro y negativo en los registros sociales disponibles por plataforma.
                </div>
                """
            )

            render_platform_sentiment_chart(gdelt_df)
            html_block(
                """
                <div class="ed-note-green">
                    Esta vista permite comparar la composición del tono en cada canal digital y ofrece una base visual más directa para la discusión académica.
                </div>
                """
            )

    with col6:
        with st.container(border=True, key="card_ed_gdelt_tono"):
            html_block(
                """
                <div class="section-title-card">Redes/medios · sentimiento</div>
                <div class="section-subtitle-card">
                    Resumen del tono o sentimiento disponible en los registros GDELT.
                </div>
                """
            )

            if gdelt_df is not None and not gdelt_df.empty:
                render_tone_card(gdelt_df)
                html_block(
                    """
                    <div class="ed-note-yellow">
                        El tono GDELT permite contextualizar la orientación emocional o valorativa de la cobertura digital observada.
                    </div>
                    """
                )
            else:
                empty_state("No se ha cargado una base GDELT con columna de tono.")

    st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)

    col7, col8 = st.columns(2, gap="large")

    with col7:
        with st.container(border=True, key="card_ed_gdelt_fuentes"):
            html_block(
                """
                <div class="section-title-card">Redes/medios · principales fuentes</div>
                <div class="section-subtitle-card">
                    Fuentes, dominios o medios con mayor presencia dentro del corpus GDELT.
                </div>
                """
            )

            if gdelt_df is not None and not gdelt_df.empty:
                render_bars(gdelt_top_sources(gdelt_df), "blue")
                html_block(
                    """
                    <div class="ed-note-blue">
                        La distribución de fuentes permite identificar concentración o diversidad de cobertura dentro del corpus externo.
                    </div>
                    """
                )
            else:
                empty_state("No se ha cargado una base GDELT con fuentes, dominios o URLs.")

    with col8:
        with st.container(border=True, key="card_ed_gdelt_keywords"):
            html_block(
                """
                <div class="section-title-card">Redes/medios · términos recurrentes</div>
                <div class="section-subtitle-card">
                    Palabras o temas frecuentes extraídos del texto, títulos, temas o resúmenes disponibles en GDELT.
                </div>
                """
            )

            if gdelt_df is not None and not gdelt_df.empty:
                render_bars(gdelt_keywords(gdelt_df), "green")
                html_block(
                    """
                    <div class="ed-note-green">
                        Los términos recurrentes ayudan a describir los ejes temáticos dominantes en la cobertura digital analizada.
                    </div>
                    """
                )
            else:
                empty_state("No se ha cargado una base GDELT con texto, títulos, temas o resúmenes.")

    st.markdown('<div class="ed-section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_ed_triangulacion"):
        html_block(
            """
            <div class="section-title-card">Triangulación entre encuesta y redes/medios</div>
            <div class="section-subtitle-card">
                Cruce interpretativo entre experiencia ciudadana declarada y señales digitales externas del ecosistema informativo.
            </div>
            """
        )

        gdelt_status = "disponible" if n_gdelt > 0 else "pendiente de carga"

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
                        El corpus de redes/medios está <strong>{gdelt_status}</strong> con <strong>{n_gdelt:,}</strong> registros.
                        Permite observar volumen, fuentes, tono y evolución temporal de la cobertura digital.
                    </div>
                </div>

                <div class="ed-source-card yellow">
                    <div class="ed-source-title">Valor analítico</div>
                    <div class="ed-source-text">
                        La triangulación no prueba causalidad, pero fortalece la interpretación sobre cómo la circulación
                        digital de información se relaciona con percepciones de manipulación, desinformación y confianza electoral.
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
                La evidencia digital integrada permite contextualizar el ecosistema informativo de la campaña desde dos fuentes complementarias.
            </div>
            """
        )

        html_block(
            f"""
            <div class="interpretation-grid">
                <div class="interpretation-box blue">
                    <div class="interpretation-value">{exposicion_diaria_pct:.1f}%</div>
                    <div class="interpretation-label">
                        estuvo expuesto a contenido político digital al menos una vez al día durante la campaña.
                    </div>
                </div>

                <div class="interpretation-box red">
                    <div class="interpretation-value">{falso_pct:.1f}%</div>
                    <div class="interpretation-label">
                        percibió contenido político falso, manipulado o generado con IA algunas o muchas veces.
                    </div>
                </div>

                <div class="interpretation-box green">
                    <div class="interpretation-value">{n_gdelt:,}</div>
                    <div class="interpretation-label">
                        registros de redes/medios disponibles para contextualizar la cobertura digital externa.
                    </div>
                </div>

                <div class="interpretation-box yellow">
                    <div class="interpretation-value">{tone_value}</div>
                    <div class="interpretation-label">
                        corresponde al tono promedio observado en registros de redes/medios válidos.
                    </div>
                </div>
            </div>

            <div class="ed-note-green">
                En conjunto, la encuesta y GDELT permiten distinguir entre percepción ciudadana y señal digital externa.
                La encuesta evidencia alta exposición, reconocimiento de automatización y percepción de contenido manipulado.
                El corpus de redes/medios, cuando se incorpora como evidencia externa, permite observar la dinámica temporal, fuentes y tono de la cobertura.
                Esta combinación fortalece la lectura metodológica del ecosistema electoral digital sin asumir causalidad directa.
            </div>
            """
        )

    st.caption(
        "Nota metodológica: esta pestaña triangula evidencia autodeclarada de encuesta con evidencia documental-digital de redes y medios. "
        "La encuesta mide percepción y experiencia ciudadana; GDELT permite contextualizar volumen, fuentes, tono y evolución temporal "
        "de registros externos. La triangulación es interpretativa y no implica inferencia causal directa."
    )