from __future__ import annotations

import json
import math
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px


ROOT = Path(__file__).resolve().parents[2]

DATA_CANDIDATES = [
    ROOT / "data" / "processed" / "encuestas" / "model_ready.csv",
    ROOT / "data" / "processed" / "model_ready.csv",
    ROOT / "backend" / "public" / "surveys" / "tables" / "model_ready.csv",
]

OUTPUT_SURVEYS = ROOT / "outputs" / "surveys"
PUBLIC_SURVEYS = ROOT / "backend" / "public" / "surveys"

TABLES_DIRS = [
    OUTPUT_SURVEYS / "tables",
    PUBLIC_SURVEYS / "tables",
]

FIGURES_DIRS = [
    OUTPUT_SURVEYS / "figures",
    PUBLIC_SURVEYS / "figures",
]


LIKERT_LABELS = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Ni de acuerdo ni en desacuerdo",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}

LIKERT_MAP = {
    "totalmente en desacuerdo": 1,
    "en desacuerdo": 2,
    "ni de acuerdo ni en desacuerdo": 3,
    "de acuerdo": 4,
    "totalmente de acuerdo": 5,
}


AGE_ORDER = ["18-24", "25-34", "35-44", "45-54", "55-64"]


# Si el detector automático no encuentra tus columnas,
# coloca aquí el nombre exacto de la columna.
COLUMN_OVERRIDES = {
    "age": "edad",
    "manipulacion_ia": "Percepción sobre el uso de IA en campañas políticas [Los partidos pueden manipular mi opinión mediante mensajes personalizados creados con IA.]",
    "bots_confianza": "Percepción sobre el uso de IA en campañas políticas [La presencia de bots o cuentas falsas en redes sociales reduce mi confianza en la información política digital.]",
    "deepfakes_desconfianza": "Percepción sobre el uso de IA en campañas políticas [La existencia de deepfakes o contenido manipulado me hace desconfiar más de las campañas políticas digitales.]",
    "frecuencia_redes": "¿Con qué frecuencia utiliza redes sociales?",
    "contenido_politico_digital": "Durante la campaña presidencial entre Luisa González y Daniel Noboa, ¿con qué frecuencia vio o recibió contenido político en redes sociales o plataformas digitales?",
    "reconocimiento_automatizacion": "percibe_automatizacion",
    "contenido_falso_manipulado": "¿Vio alguna vez un video, imagen, audio o noticia política de la campaña entre Luisa González y Daniel Noboa que le pareció “falso”, “manipulado” o generado con IA?",
}


def normalize_text(value: object) -> str:
    text = str(value).strip().lower()
    text = text.replace("–", "-").replace("—", "-")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = " ".join(text.split())
    return text


def find_data_file() -> Path:
    for path in DATA_CANDIDATES:
        if path.exists():
            return path

    raise FileNotFoundError(
        "No se encontró el archivo de encuesta procesado. "
        "Revisa si existe data/processed/encuestas/model_ready.csv"
    )


def find_column(df: pd.DataFrame, logical_name: str, keyword_groups: list[list[str]]) -> str:
    override = COLUMN_OVERRIDES.get(logical_name)

    if override:
        if override in df.columns:
            return override
        raise KeyError(f"La columna definida en override no existe: {override}")

    normalized_columns = {col: normalize_text(col) for col in df.columns}

    for col, norm_col in normalized_columns.items():
        for keywords in keyword_groups:
            if all(keyword in norm_col for keyword in keywords):
                return col

    print("\nColumnas disponibles en el archivo:")
    for col in df.columns:
        print(f"- {col}")

    raise KeyError(
        f"No se pudo identificar automáticamente la columna para: {logical_name}. "
        f"Agrega el nombre exacto en COLUMN_OVERRIDES."
    )


def normalize_age(value: object) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip()
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace(" ", "")

    return text


def convert_likert(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    return series.apply(lambda x: LIKERT_MAP.get(normalize_text(x), None))

def convert_social_frequency(series: pd.Series) -> pd.Series:
    """
    Convierte frecuencias de uso/exposición digital a escala 1-5.
    1 = mínima exposición
    5 = máxima exposición
    """
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    def map_value(value):
        text = normalize_text(value)

        if "varias veces al dia" in text:
            return 5
        if "una vez al dia" in text:
            return 4
        if "varias veces a la semana" in text:
            return 3
        if "rara vez" in text:
            return 2
        if "nunca" in text:
            return 1

        return None

    return series.apply(map_value)


def convert_automation_recognition(series: pd.Series) -> pd.Series:
    """
    Convierte reconocimiento de herramientas automatizadas a escala 1-5.
    """
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    def map_value(value):
        text = normalize_text(value)

        if "claramente" in text:
            return 5
        if "tal vez" in text or "no estoy seguro" in text:
            return 3
        if text == "no":
            return 1

        return None

    return series.apply(map_value)


def convert_fake_content_seen(series: pd.Series) -> pd.Series:
    """
    Convierte exposición a contenido falso/manipulado/generado con IA a escala 1-5.
    """
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    def map_value(value):
        text = normalize_text(value)

        if "muchas veces" in text:
            return 5
        if "algunas veces" in text:
            return 4
        if "no estoy seguro" in text:
            return 3
        if text == "no":
            return 1

        return None

    return series.apply(map_value)


def exposure_interpretation(value: float) -> str:
    if pd.isna(value):
        return "Sin datos"
    if value >= 4:
        return "Alta exposición digital"
    if value >= 3:
        return "Exposición digital moderada"
    return "Baja exposición digital"


def build_exposure_index_by_age(
    df: pd.DataFrame,
    group_col: str,
    order: list[str],
) -> pd.DataFrame:
    summary = (
        df.groupby(group_col, observed=True)["indice_exposicion_digital"]
        .agg(
            n="count",
            indice_promedio="mean",
            desviacion_estandar="std",
        )
        .reset_index()
        .rename(columns={group_col: "rango_edad"})
    )

    summary["error_estandar"] = summary.apply(
        lambda row: row["desviacion_estandar"] / math.sqrt(row["n"])
        if row["n"] > 0 and not pd.isna(row["desviacion_estandar"])
        else 0,
        axis=1,
    )

    summary["interpretacion"] = summary["indice_promedio"].apply(exposure_interpretation)

    summary["rango_edad"] = pd.Categorical(
        summary["rango_edad"],
        categories=order,
        ordered=True,
    )

    summary = summary.sort_values("rango_edad").reset_index(drop=True)

    summary["indice_promedio"] = summary["indice_promedio"].round(3)
    summary["desviacion_estandar"] = summary["desviacion_estandar"].round(3)
    summary["error_estandar"] = summary["error_estandar"].round(3)

    return summary


def interpretation(value: float) -> str:
    if pd.isna(value):
        return "Sin datos"
    if value >= 4:
        return "Alta percepción de riesgo"
    if value >= 3:
        return "Percepción de riesgo moderada"
    return "Baja percepción de riesgo"


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    age_col = find_column(
        df,
        "age",
        [
            ["rango", "edad"],
            ["edad"],
            ["cual", "edad"],
        ],
    )

    manipulacion_col = find_column(
        df,
        "manipulacion_ia",
        [
            ["manipular", "opinion", "ia"],
            ["mensajes", "personalizados", "ia"],
            ["partidos", "manipular", "opinion"],
        ],
    )

    bots_col = find_column(
        df,
        "bots_confianza",
        [
            ["bots", "confianza"],
            ["cuentas", "falsas", "confianza"],
            ["presencia", "bots", "reduce"],
        ],
    )

    deepfakes_col = find_column(
        df,
        "deepfakes_desconfianza",
        [
            ["deepfakes", "desconfiar"],
            ["deepfake", "desconfianza"],
            ["contenido", "manipulado", "desconfiar"],
            ["existencia", "deepfakes"],
        ],
    )

    frecuencia_redes_col = find_column(
        df,
        "frecuencia_redes",
        [
            ["frecuencia", "utiliza", "redes", "sociales"],
            ["utiliza", "redes", "sociales"],
        ],
    )

    contenido_politico_col = find_column(
        df,
        "contenido_politico_digital",
        [
            ["frecuencia", "contenido", "politico", "redes"],
            ["vio", "recibio", "contenido", "politico"],
            ["contenido", "politico", "plataformas", "digitales"],
        ],
    )

    automatizacion_col = find_column(
        df,
        "reconocimiento_automatizacion",
        [
            ["reconocio", "herramientas", "automatizadas"],
            ["bots", "anuncios", "personalizados", "deepfakes"],
            ["herramientas", "automatizadas"],
        ],
    )

    contenido_falso_col = find_column(
        df,
        "contenido_falso_manipulado",
        [
            ["parecio", "falso", "manipulado"],
            ["video", "imagen", "audio", "noticia", "falso"],
            ["generado", "ia"],
        ],
    )

    out = df.copy()

    out["rango_edad"] = out[age_col].apply(normalize_age)

    out["manipulacion_ia_num"] = convert_likert(out[manipulacion_col])
    out["bots_confianza_num"] = convert_likert(out[bots_col])
    out["deepfakes_desconfianza_num"] = convert_likert(out[deepfakes_col])

    out["indice_riesgo_ia"] = out[
        [
            "manipulacion_ia_num",
            "bots_confianza_num",
            "deepfakes_desconfianza_num",
        ]
    ].mean(axis=1)


    out["frecuencia_redes_num"] = convert_social_frequency(out[frecuencia_redes_col])
    out["contenido_politico_num"] = convert_social_frequency(out[contenido_politico_col])
    out["automatizacion_num"] = convert_automation_recognition(out[automatizacion_col])
    out["contenido_falso_num"] = convert_fake_content_seen(out[contenido_falso_col])

    out["indice_exposicion_digital"] = out[
        [
            "frecuencia_redes_num",
            "contenido_politico_num",
            "automatizacion_num",
            "contenido_falso_num",
        ]
    ].mean(axis=1)

    # Filtrado de rangos válidos
    # =========================================================
    out = out[out["rango_edad"].isin(AGE_ORDER)].copy()

    # =========================================================
    # Agrupación robusta por edad
    # =========================================================
    out["grupo_edad_robusto"] = out["rango_edad"].replace(
        {
            "18-24": "18-24",
            "25-34": "25-34",
            "35-44": "35-64",
            "45-54": "35-64",
            "55-64": "35-64",
        }
    )


    return out


def build_risk_index_by_age(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("rango_edad", observed=True)["indice_riesgo_ia"]
        .agg(
            n="count",
            indice_promedio="mean",
            desviacion_estandar="std",
        )
        .reset_index()
    )

    summary["error_estandar"] = summary.apply(
        lambda row: row["desviacion_estandar"] / math.sqrt(row["n"])
        if row["n"] > 0 and not pd.isna(row["desviacion_estandar"])
        else 0,
        axis=1,
    )

    summary["interpretacion"] = summary["indice_promedio"].apply(interpretation)

    summary["rango_edad"] = pd.Categorical(
        summary["rango_edad"],
        categories=AGE_ORDER,
        ordered=True,
    )

    summary = summary.sort_values("rango_edad").reset_index(drop=True)

    summary["indice_promedio"] = summary["indice_promedio"].round(3)
    summary["desviacion_estandar"] = summary["desviacion_estandar"].round(3)
    summary["error_estandar"] = summary["error_estandar"].round(3)

    return summary


def build_deepfake_distribution_by_age(df: pd.DataFrame) -> pd.DataFrame:
    temp = df.dropna(subset=["deepfakes_desconfianza_num"]).copy()
    temp["respuesta_valor"] = temp["deepfakes_desconfianza_num"].astype(int)
    temp["respuesta_texto"] = temp["respuesta_valor"].map(LIKERT_LABELS)

    table = (
        temp.groupby(["rango_edad", "respuesta_valor", "respuesta_texto"], observed=True)
        .size()
        .reset_index(name="frecuencia")
    )

    table["total_rango"] = table.groupby("rango_edad")["frecuencia"].transform("sum")
    table["porcentaje"] = (table["frecuencia"] / table["total_rango"] * 100).round(2)

    table["rango_edad"] = pd.Categorical(
        table["rango_edad"],
        categories=AGE_ORDER,
        ordered=True,
    )

    table["respuesta_texto"] = pd.Categorical(
        table["respuesta_texto"],
        categories=[LIKERT_LABELS[i] for i in range(1, 6)],
        ordered=True,
    )

    table = table.sort_values(["rango_edad", "respuesta_valor"]).reset_index(drop=True)

    return table


def save_table(df: pd.DataFrame, filename: str) -> None:
    for directory in TABLES_DIRS:
        directory.mkdir(parents=True, exist_ok=True)
        df.to_csv(directory / filename, index=False, encoding="utf-8-sig")


def save_figure(fig, filename_stem: str) -> None:
    for directory in FIGURES_DIRS:
        directory.mkdir(parents=True, exist_ok=True)

        html_path = directory / f"{filename_stem}.html"
        fig.write_html(html_path, include_plotlyjs="cdn")

        png_path = directory / f"{filename_stem}.png"

        try:
            fig.write_image(png_path, scale=2)
        except Exception as exc:
            print(
                f"No se pudo exportar PNG para {filename_stem}. "
                f"Se generó HTML correctamente. "
                f"Si necesitas PNG, instala kaleido: pip install -U kaleido"
            )
            print(f"Detalle: {exc}")


def create_risk_index_figure(summary: pd.DataFrame):
    fig = px.bar(
        summary,
        x="rango_edad",
        y="indice_promedio",
        error_y="error_estandar",
        text="indice_promedio",
        labels={
            "rango_edad": "Rango de edad",
            "indice_promedio": "Índice promedio de percepción de riesgo por IA",
        },
        title="Índice de percepción de riesgo por IA en campañas políticas digitales según rangos de edad",
        category_orders={"rango_edad": AGE_ORDER},
    )

    fig.update_yaxes(range=[1, 5], dtick=1)
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=480,
        margin=dict(l=30, r=30, t=80, b=40),
        title_x=0.02,
    )

    return fig


def create_deepfake_distribution_figure(table: pd.DataFrame):
    fig = px.bar(
        table,
        x="rango_edad",
        y="porcentaje",
        color="respuesta_texto",
        barmode="stack",
        text=table["porcentaje"].round(1).astype(str) + "%",
        labels={
            "rango_edad": "Rango de edad",
            "porcentaje": "Porcentaje de respuestas",
            "respuesta_texto": "Escala Likert",
        },
        title="Distribución porcentual de respuestas sobre deepfakes y desconfianza según rangos de edad",
        category_orders={
            "rango_edad": AGE_ORDER,
            "respuesta_texto": [LIKERT_LABELS[i] for i in range(1, 6)],
        },
    )

    fig.update_yaxes(ticksuffix="%", range=[0, 100])
    fig.update_layout(
        height=520,
        margin=dict(l=30, r=30, t=80, b=40),
        legend_title_text="Nivel de respuesta",
        title_x=0.02,
    )

    return fig






def update_manifest() -> None:
    PUBLIC_SURVEYS.mkdir(parents=True, exist_ok=True)

    manifest_path = PUBLIC_SURVEYS / "MANIFEST.json"

    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
    else:
        manifest = {}

    manifest["age_risk_analysis"] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "description": "Análisis de percepción de riesgo por IA y deepfakes según rangos de edad.",
        "tables": {
            "risk_index_by_age": "tables/risk_index_by_age.csv",
            "deepfake_distrust_by_age": "tables/deepfake_distrust_by_age.csv",
            "exposure_index_by_age": "tables/exposure_index_by_age.csv",
            "exposure_index_by_age_robust": "tables/exposure_index_by_age_robust.csv",
        },
        "figures": {
            "risk_index_by_age_html": "figures/risk_index_by_age.html",
            "risk_index_by_age_png": "figures/risk_index_by_age.png",
            "deepfake_distrust_by_age_html": "figures/deepfake_distrust_by_age.html",
            "deepfake_distrust_by_age_png": "figures/deepfake_distrust_by_age.png",
        },
    }

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    manifest_txt = PUBLIC_SURVEYS / "MANIFEST.txt"
    manifest_txt.write_text(
        "Artefactos de encuestas publicados\n"
        "----------------------------------\n"
        "tables/risk_index_by_age.csv\n"
        "tables/deepfake_distrust_by_age.csv\n"
        "tables/exposure_index_by_age.csv\n"
        "tables/exposure_index_by_age_robust.csv\n"
        "figures/risk_index_by_age.html\n"
        "figures/risk_index_by_age.png\n"
        "figures/deepfake_distrust_by_age.html\n"
        "figures/deepfake_distrust_by_age.png\n",
        encoding="utf-8",
    )





def main() -> None:
    data_file = find_data_file()
    print(f"Leyendo encuesta procesada desde: {data_file}")

    df = pd.read_csv(data_file, encoding="utf-8-sig")
    prepared = prepare_dataframe(df)

    if prepared.empty:
        raise ValueError("No hay datos válidos para los rangos de edad esperados.")

    risk_summary = build_risk_index_by_age(prepared)
    deepfake_distribution = build_deepfake_distribution_by_age(prepared)


    exposure_by_age = build_exposure_index_by_age(
        prepared,
        group_col="rango_edad",
        order=["18-24", "25-34", "35-44", "45-54", "55-64"],
    )

    exposure_by_age_robust = build_exposure_index_by_age(
        prepared,
        group_col="grupo_edad_robusto",
        order=["18-24", "25-34", "35-64"],
    )

    save_table(risk_summary, "risk_index_by_age.csv")
    save_table(deepfake_distribution, "deepfake_distrust_by_age.csv")
    save_table(exposure_by_age, "exposure_index_by_age.csv")
    save_table(exposure_by_age_robust, "exposure_index_by_age_robust.csv")

    risk_fig = create_risk_index_figure(risk_summary)
    deepfake_fig = create_deepfake_distribution_figure(deepfake_distribution)

    save_figure(risk_fig, "risk_index_by_age")
    save_figure(deepfake_fig, "deepfake_distrust_by_age")

    update_manifest()

    print("\nArchivos generados correctamente:")
    print("- outputs/surveys/tables/risk_index_by_age.csv")
    print("- outputs/surveys/tables/deepfake_distrust_by_age.csv")
    print("- outputs/surveys/figures/risk_index_by_age.html")
    print("- outputs/surveys/figures/deepfake_distrust_by_age.html")
    print("- backend/public/surveys/tables/risk_index_by_age.csv")
    print("- backend/public/surveys/tables/deepfake_distrust_by_age.csv")
    print("- backend/public/surveys/figures/risk_index_by_age.html")
    print("- backend/public/surveys/figures/deepfake_distrust_by_age.html")
    print("- outputs/surveys/tables/exposure_index_by_age.csv")
    print("- outputs/surveys/tables/exposure_index_by_age_robust.csv")
    print("- backend/public/surveys/tables/exposure_index_by_age.csv")
    print("- backend/public/surveys/tables/exposure_index_by_age_robust.csv")





if __name__ == "__main__":
    main()