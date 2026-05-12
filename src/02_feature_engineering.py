import pandas as pd
import numpy as np
from pathlib import Path

# RUTAS (encuestas)
INPUT_PATH = Path("data/processed/encuestas/respuestas_limpias.csv")
OUTPUT_DIR = Path("data/processed/encuestas")
OUTPUT_PATH = OUTPUT_DIR / "model_ready.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================
# Leer datos procesados
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
df.columns = df.columns.str.strip()

print("Filas iniciales:", df.shape[0])

likert_map = {
    "Totalmente en desacuerdo": 1,
    "En desacuerdo": 2,
    "Ni de acuerdo ni en desacuerdo": 3,
    "De acuerdo": 4,
    "Totalmente de acuerdo": 5,
}

def map_likert(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.replace("\xa0", " ").str.strip()
    return s.map(likert_map)

# Validación temprana para evitar KeyError silencioso
required = ["confianza_limpieza", "confianza_fraude"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise KeyError(
        f"Faltan columnas requeridas: {missing}. Columnas actuales: {df.columns.tolist()}"
    )

# ============================
# Target / índices
df["limpieza_num"] = map_likert(df["confianza_limpieza"])
df["fraude_num"] = map_likert(df["confianza_fraude"])

df["fraude_rev"] = 6 - df["fraude_num"]
df["confianza_idx"] = (df["limpieza_num"] + df["fraude_rev"]) / 2
df["confianza_idx_round"] = df["confianza_idx"].round().astype("Int64")

mask_invalid = df[["limpieza_num", "fraude_num"]].isna().any(axis=1)
print("Filas con valores no válidos en limpieza_num o fraude_num:", int(mask_invalid.sum()))

if mask_invalid.any():
    print("\nEjemplos de filas problemáticas (texto original):")
    print(df.loc[mask_invalid, ["confianza_limpieza", "confianza_fraude"]].head(20))

# Target alterno (3 clases) para comparar modelos (1-2=1, 3=2, 4-5=3)
def to_3_classes(x):
    if pd.isna(x):
        return pd.NA
    x = int(x)
    if x <= 2:
        return 1
    if x == 3:
        return 2
    return 3

df["confianza_3"] = df["confianza_idx_round"].apply(to_3_classes).astype("Int64")

# ============================
# Validación simple del índice
# ============================

corr_confianza = df[["limpieza_num", "fraude_rev"]].corr().iloc[0, 1]

if abs(corr_confianza) >= 0.70:
    interpretacion_corr = "correlación fuerte"
elif abs(corr_confianza) >= 0.40:
    interpretacion_corr = "correlación moderada"
else:
    interpretacion_corr = "correlación débil"


indice_validacion = pd.DataFrame([{
    "indicador_1": "limpieza_num",
    "indicador_2": "fraude_rev",
    "correlacion": round(corr_confianza, 4),
    "interpretacion": f"{interpretacion_corr} entre los ítems utilizados para construir el índice operativo de confianza electoral"
}])

indice_validacion.to_csv(
    OUTPUT_DIR / "validacion_indice_confianza.csv",
    index=False,
    encoding="utf-8-sig"
)

# ============================
# Features Likert (Percepción IA) -> numéricas
# (más robusto que startswith por si cambia el texto exacto)
likert_cols = [c for c in df.columns if "Percepción sobre el uso de IA en campañas políticas" in c]

for c in likert_cols:
    df[c + "_num"] = map_likert(df[c])

# ============================
# Feature NLP: Longitud + palabras de respuesta abierta
text_col = (
    "¿Qué recomendaciones haría para garantizar un uso responsable y transparente de la "
    "inteligencia artificial en campañas políticas digitales en Ecuador, considerando la "
    "experiencia de la campaña entre Luisa González y Daniel Noboa?"
)

if text_col in df.columns:
    txt = df[text_col].fillna("").astype(str)
    df["longitud_recomendacion"] = txt.str.len()
    df["palabras_recomendacion"] = txt.str.split().str.len()
    print("Features NLP creadas: longitud_recomendacion, palabras_recomendacion")


# ============================
# Tabla de construcción del índice para anexos
# ============================

cols_indice = [
    "confianza_limpieza",
    "confianza_fraude",
    "limpieza_num",
    "fraude_num",
    "fraude_rev",
    "confianza_idx",
    "confianza_idx_round",
    "confianza_3"
]

tabla_indice = df[cols_indice].copy()
tabla_indice.to_csv(
    OUTPUT_DIR / "tabla_construccion_indice_confianza.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================
# Distribución de clases
# ============================

dist_5 = (
    df["confianza_idx_round"]
    .value_counts(dropna=False)
    .sort_index()
    .reset_index()
)

dist_5.columns = ["nivel_confianza", "frecuencia"]

dist_5["porcentaje"] = (
    dist_5["frecuencia"] / dist_5["frecuencia"].sum() * 100
).round(2)

dist_5.to_csv(
    OUTPUT_DIR / "distribucion_confianza_5niveles.csv",
    index=False,
    encoding="utf-8-sig"
)

dist_3 = (
    df["confianza_3"]
    .value_counts(dropna=False)
    .sort_index()
    .reset_index()
)

dist_3.columns = ["nivel_confianza", "frecuencia"]

dist_3["porcentaje"] = (
    dist_3["frecuencia"] / dist_3["frecuencia"].sum() * 100
).round(2)

dist_3.to_csv(
    OUTPUT_DIR / "distribucion_confianza_3clases.csv",
    index=False,
    encoding="utf-8-sig"
)


diccionario_variables = pd.DataFrame([
    {
        "variable": "limpieza_num",
        "descripcion": "Codificación numérica del ítem sobre transparencia electoral",
        "escala": "Likert 1-5"
    },
    {
        "variable": "fraude_num",
        "descripcion": "Codificación numérica del ítem sobre percepción de fraude",
        "escala": "Likert 1-5"
    },
    {
        "variable": "fraude_rev",
        "descripcion": "Codificación inversa del ítem de fraude",
        "escala": "Likert invertida 1-5"
    },
    {
        "variable": "confianza_idx",
        "descripcion": "Índice operativo de confianza electoral calculado como promedio de limpieza_num y fraude_rev",
        "escala": "Continua ordinal 1-5"
    },
    {
        "variable": "confianza_idx_round",
        "descripcion": "Índice de confianza electoral redondeado a cinco niveles",
        "escala": "Ordinal 1-5"
    },
    {
        "variable": "confianza_3",
        "descripcion": "Variable agregada de confianza electoral: baja, media y alta",
        "escala": "Ordinal 1-3"
    },
])

diccionario_variables.to_csv(
    OUTPUT_DIR / "diccionario_variables_creadas.csv",
    index=False,
    encoding="utf-8-sig"
)

# ============================
# Dataset final para modelado
df_model = df.dropna(subset=["confianza_idx_round"]).copy()


# ============================
# Reporte de missing
# ============================
missing_df = pd.DataFrame({
    "variable": df.columns,
    "n_missing": df.isna().sum().values,
    "pct_missing": (df.isna().mean() * 100).round(2).values
}).sort_values("pct_missing", ascending=False)

missing_df.to_csv(OUTPUT_DIR / "missing_report.csv", index=False, encoding="utf-8-sig")


# ============================
# Distribución del target (5 clases)
# ============================
dist_5 = df_model["confianza_idx_round"].value_counts().sort_index()
dist_5_df = pd.DataFrame({
    "nivel_confianza": dist_5.index,
    "n": dist_5.values,
    "porcentaje": (dist_5.values / dist_5.sum() * 100).round(2),
})
dist_5_df.to_csv(OUTPUT_DIR / "target_distribution_5.csv", index=False, encoding="utf-8-sig")


# ============================
# Distribución del target (3 clases)
# ============================
dist_3 = df_model["confianza_3"].value_counts().sort_index()
dist_3_df = pd.DataFrame({
    "nivel_confianza": dist_3.index,
    "n": dist_3.values,
    "porcentaje": (dist_3.values / dist_3.sum() * 100).round(2)
})
dist_3_df.to_csv(OUTPUT_DIR / "tabla_distribucion_confianza_3clases.csv", index=False)



num_created = [c for c in df_model.columns if c.endswith("_num")]
print("Nuevas columnas numéricas (_num):", len(num_created))
print("Ejemplo:", num_created[:5])

print("Filas válidas para modelado:", df_model.shape[0])

df_model.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print("Archivo guardado en:", OUTPUT_PATH)


# ============================
# Versión sin variables textuales derivadas
# ============================
OUTPUT_PATH_NO_TEXT = OUTPUT_DIR / "model_ready_no_text.csv"

df_model_no_text = df_model.drop(
    columns=["longitud_recomendacion", "palabras_recomendacion"],
    errors="ignore"
).copy()

df_model_no_text.to_csv(OUTPUT_PATH_NO_TEXT, index=False, encoding="utf-8-sig")
print("Archivo sin variables textuales guardado en:", OUTPUT_PATH_NO_TEXT)


#============================
# Vista previa de variables clave
print("\nVista previa:")
cols_preview = [
    "confianza_limpieza", "confianza_fraude",
    "limpieza_num", "fraude_num", "fraude_rev",
    "confianza_idx", "confianza_idx_round", "confianza_3"
]
print(df_model[cols_preview].head())


# ============================
# Resumen metodológico
# ============================

resumen_indice = pd.DataFrame([{
    "indice": "confianza_idx",
    "tipo": "Índice operativo ordinal",
    "metodo": "Promedio entre limpieza_num y fraude_rev",
    "escala_original": "Likert 1-5",
    "versiones_generadas": "5 niveles y 3 clases",
    "nota": "La versión de 3 clases se utilizó para estabilizar el modelado predictivo."
}])

resumen_indice.to_csv(
    OUTPUT_DIR / "resumen_metodologico_indice.csv",
    index=False,
    encoding="utf-8-sig"
)

