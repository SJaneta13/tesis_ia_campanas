from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

DATA_SURVEY = ROOT / "data" / "processed" / "encuestas" / "model_ready.csv"
OUTPUT_DIR = ROOT / "outputs" / "latest" / "tables"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"[WARN] No existe: {path}")
        return pd.DataFrame()

    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin1")
    except Exception as exc:
        print(f"[ERROR] No se pudo leer {path}: {exc}")
        return pd.DataFrame()


def normalize_name(value: str) -> str:
    return (
        str(value)
        .lower()
        .strip()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
    )


def find_first_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    if df.empty:
        return None

    normalized_cols = {normalize_name(col): col for col in df.columns}

    for candidate in candidates:
        candidate_norm = normalize_name(candidate)
        if candidate_norm in normalized_cols:
            return normalized_cols[candidate_norm]

    for col in df.columns:
        col_norm = normalize_name(col)
        for candidate in candidates:
            if normalize_name(candidate) in col_norm:
                return col

    return None


def infer_variable_type(series: pd.Series) -> str:
    numeric = pd.to_numeric(series, errors="coerce")

    if numeric.notna().mean() >= 0.8:
        unique_count = numeric.dropna().nunique()

        if unique_count <= 6:
            return "Ordinal / discreta"

        return "Numérica"

    unique_count = series.dropna().astype(str).str.strip().nunique()

    if unique_count <= 15:
        return "Categórica"

    return "Texto / categórica abierta"


def infer_construct(col: str) -> str:
    c = normalize_name(col)

    if any(x in c for x in ["edad", "genero", "sexo", "facultad", "rol", "residencia", "quito"]):
        return "Perfil sociodemográfico"

    if any(x in c for x in ["confianza", "transparencia", "fraude", "manipulacion electoral"]):
        return "Confianza electoral"

    if any(x in c for x in ["ia", "inteligencia artificial", "automatizado", "bot", "deepfake", "algoritmo"]):
        return "Percepción sobre IA en campañas"

    if any(x in c for x in ["verifica", "fuente", "noticia", "falso", "alfabetizacion"]):
        return "Alfabetización mediática"

    if any(x in c for x in ["regulacion", "regular", "control", "ley"]):
        return "Regulación y transparencia"

    return "Variable complementaria"


def infer_use(col: str) -> str:
    c = normalize_name(col)

    if "confianza_idx" in c or "confianza" in c:
        return "Variable dependiente / indicador principal"

    if any(x in c for x in ["edad", "genero", "sexo", "facultad", "rol", "residencia", "quito"]):
        return "Segmentación / filtro"

    if any(x in c for x in ["ia", "bot", "deepfake", "automatizado", "microsegmentacion", "algoritmo"]):
        return "Predictora perceptual"

    if any(x in c for x in ["regulacion", "regular", "control"]):
        return "Recomendaciones / análisis institucional"

    return "Análisis descriptivo"


def build_data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    total_rows = len(df)
    total_cols = len(df.columns)

    duplicate_rows = int(df.duplicated().sum()) if not df.empty else 0

    rows.append({
        "Indicador": "Registros válidos cargados",
        "Valor": total_rows,
        "Interpretación": "Número de observaciones disponibles en la base procesada."
    })

    rows.append({
        "Indicador": "Variables disponibles",
        "Valor": total_cols,
        "Interpretación": "Número de columnas disponibles para análisis descriptivo y modelado."
    })

    rows.append({
        "Indicador": "Registros duplicados exactos",
        "Valor": duplicate_rows,
        "Interpretación": "Filas idénticas detectadas en la base procesada."
    })

    if total_rows > 0 and total_cols > 0:
        total_cells = total_rows * total_cols
        missing_cells = int(df.isna().sum().sum())
        completeness = round((1 - missing_cells / total_cells) * 100, 2)

        rows.append({
            "Indicador": "Completitud general de la base (%)",
            "Valor": completeness,
            "Interpretación": "Porcentaje de celdas no vacías en la base procesada."
        })

    edad_col = find_first_column(df, ["edad", "rango de edad", "¿cuál es tu edad?"])

    if edad_col:
        rows.append({
            "Indicador": "Variable de edad detectada",
            "Valor": edad_col,
            "Interpretación": "La población del estudio se interpreta bajo el alcance 18 a 64 años."
        })

    confianza_col = find_first_column(df, ["confianza_idx_round", "confianza_idx", "confianza electoral"])

    if confianza_col:
        valid_conf = pd.to_numeric(df[confianza_col], errors="coerce").notna().sum()

        rows.append({
            "Indicador": "Registros con índice de confianza válido",
            "Valor": int(valid_conf),
            "Interpretación": "Casos utilizables para análisis de confianza electoral."
        })

    return pd.DataFrame(rows)


def build_variable_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for col in df.columns:
        series = df[col]

        rows.append({
            "Variable": col,
            "Tipo inferido": infer_variable_type(series),
            "Constructo asociado": infer_construct(col),
            "Uso en la plataforma": infer_use(col),
            "Valores no nulos": int(series.notna().sum()),
            "Valores nulos": int(series.isna().sum()),
            "Valores únicos": int(series.dropna().astype(str).str.strip().nunique()),
        })

    return pd.DataFrame(rows)


def build_construct_map(df: pd.DataFrame) -> pd.DataFrame:
    candidate_rows = [
        {
            "Constructo teórico": "Perfil sociodemográfico",
            "Variable esperada": "edad / rango de edad",
            "Módulo": "Perfil de la muestra",
            "Uso metodológico": "Segmentación de resultados para comparar grupos entre 18 y 64 años."
        },
        {
            "Constructo teórico": "Perfil sociodemográfico",
            "Variable esperada": "género / rol / facultad / residencia",
            "Módulo": "Perfil de la muestra",
            "Uso metodológico": "Caracterización de la comunidad universitaria encuestada."
        },
        {
            "Constructo teórico": "Conocimiento de IA",
            "Variable esperada": "conocimiento / reconocimiento de IA",
            "Módulo": "Conocimiento de IA",
            "Uso metodológico": "Medir familiaridad con herramientas de IA aplicadas a campañas políticas."
        },
        {
            "Constructo teórico": "Exposición percibida a IA",
            "Variable esperada": "bots / deepfakes / automatización / microsegmentación",
            "Módulo": "Percepción ciudadana",
            "Uso metodológico": "Variable predictora perceptual vinculada con la hipótesis H1."
        },
        {
            "Constructo teórico": "Alfabetización mediática",
            "Variable esperada": "verificación de fuentes / identificación de contenido falso",
            "Módulo": "Conocimiento de IA / Triangulación",
            "Uso metodológico": "Variable moderadora de la hipótesis H2."
        },
        {
            "Constructo teórico": "Confianza electoral",
            "Variable esperada": "confianza_idx / confianza_idx_round",
            "Módulo": "Confianza electoral / Modelos predictivos",
            "Uso metodológico": "Variable dependiente principal del estudio."
        },
        {
            "Constructo teórico": "Regulación y transparencia",
            "Variable esperada": "regulación / control / transparencia",
            "Módulo": "Percepción ciudadana / Triangulación",
            "Uso metodológico": "Base para recomendaciones técnicas e institucionales."
        },
    ]

    return pd.DataFrame(candidate_rows)


def build_triangulation_matrix() -> pd.DataFrame:
    rows = [
        {
            "Dimensión": "Bots y automatización",
            "Evidencia de encuesta": "Percepción de cuentas automatizadas y pérdida de confianza por bots.",
            "Evidencia digital": "Noticias o publicaciones con términos asociados a bots, automatización o amplificación artificial.",
            "Evidencia de modelo": "Variables de exposición o percepción de automatización pueden aparecer como predictoras.",
            "Nivel de triangulación": "Fuerte si coincide encuesta, corpus digital y modelo.",
            "Lectura para tesis": "Refuerza la hipótesis H1 sobre exposición percibida y confianza electoral."
        },
        {
            "Dimensión": "Deepfakes y contenido sintético",
            "Evidencia de encuesta": "Desconfianza frente a imágenes, audios o videos políticos manipulados con IA.",
            "Evidencia digital": "Menciones o narrativas públicas sobre contenido sintético, manipulación audiovisual o IA generativa.",
            "Evidencia de modelo": "Variables de desconfianza ante deepfakes pueden asociarse con baja confianza.",
            "Nivel de triangulación": "Media o fuerte según disponibilidad del corpus.",
            "Lectura para tesis": "Sustenta el riesgo de deterioro de la confianza informativa."
        },
        {
            "Dimensión": "Microsegmentación política",
            "Evidencia de encuesta": "Aceptación o rechazo de mensajes políticos personalizados sin transparencia.",
            "Evidencia digital": "Contexto de publicidad digital, segmentación y campañas intensivas en redes.",
            "Evidencia de modelo": "Variables de aceptación o rechazo pueden aportar al modelo predictivo.",
            "Nivel de triangulación": "Media.",
            "Lectura para tesis": "Refuerza la discusión sobre opacidad y transparencia de campañas digitales."
        },
        {
            "Dimensión": "Alfabetización mediática",
            "Evidencia de encuesta": "Capacidad declarada para verificar fuentes e identificar contenido manipulado.",
            "Evidencia digital": "No aplica como medición directa; sirve para interpretar vulnerabilidad informativa.",
            "Evidencia de modelo": "Puede actuar como variable moderadora de la relación entre IA percibida y confianza.",
            "Nivel de triangulación": "Exploratoria.",
            "Lectura para tesis": "Refuerza la hipótesis H2 y la necesidad de educación digital."
        },
        {
            "Dimensión": "Regulación y transparencia",
            "Evidencia de encuesta": "Demanda de regulación, rotulado y control del uso de IA en campañas.",
            "Evidencia digital": "Debate público sobre transparencia electoral, publicidad digital y desinformación.",
            "Evidencia de modelo": "No necesariamente predictora directa; alimenta recomendaciones.",
            "Nivel de triangulación": "Normativa / contextual.",
            "Lectura para tesis": "Soporta recomendaciones institucionales y técnicas."
        },
    ]

    return pd.DataFrame(rows)


def build_recommendation_rules() -> pd.DataFrame:
    rows = [
        {
            "Condición analítica": "Alta desconfianza asociada a bots",
            "Recomendación técnica": "Implementar monitoreo de patrones de automatización, repetición de mensajes y actividad anómala.",
            "Actor sugerido": "Universidades / CNE / observatorios digitales",
            "Tipo": "Técnica"
        },
        {
            "Condición analítica": "Alta desconfianza ante deepfakes",
            "Recomendación técnica": "Promover rotulado visible de contenido sintético y alfabetización sobre verificación audiovisual.",
            "Actor sugerido": "CNE / plataformas / universidades",
            "Tipo": "Institucional y educativa"
        },
        {
            "Condición analítica": "Baja alfabetización mediática",
            "Recomendación técnica": "Diseñar campañas formativas sobre verificación de fuentes, IA generativa y señales de manipulación.",
            "Actor sugerido": "Universidades",
            "Tipo": "Académica"
        },
        {
            "Condición analítica": "Baja confianza electoral",
            "Recomendación técnica": "Fortalecer transparencia sobre propaganda digital, responsables de anuncios y criterios de segmentación.",
            "Actor sugerido": "CNE / partidos políticos",
            "Tipo": "Institucional"
        },
        {
            "Condición analítica": "Alta preocupación por microsegmentación",
            "Recomendación técnica": "Crear lineamientos de trazabilidad sobre publicidad política personalizada.",
            "Actor sugerido": "CNE / legisladores / plataformas",
            "Tipo": "Normativa"
        },
    ]

    return pd.DataFrame(rows)


def main():
    df = read_csv_safe(DATA_SURVEY)

    if df.empty:
        print("[ERROR] No se pudo construir artefactos porque model_ready.csv está vacío o no existe.")
        return

    artifacts = {
        "data_quality_report.csv": build_data_quality_report(df),
        "variable_dictionary.csv": build_variable_dictionary(df),
        "construct_map.csv": build_construct_map(df),
        "triangulation_matrix.csv": build_triangulation_matrix(),
        "recommendation_rules.csv": build_recommendation_rules(),
    }

    for filename, artifact_df in artifacts.items():
        out_path = OUTPUT_DIR / filename
        artifact_df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"[OK] Generado: {out_path}")


if __name__ == "__main__":
    main()