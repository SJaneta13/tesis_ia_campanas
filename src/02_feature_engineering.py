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
# Dataset final para modelado
df_model = df.dropna(subset=["confianza_idx_round"]).copy()

num_created = [c for c in df_model.columns if c.endswith("_num")]
print("Nuevas columnas numéricas (_num):", len(num_created))
print("Ejemplo:", num_created[:5])

print("Filas válidas para modelado:", df_model.shape[0])

df_model.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print("Archivo guardado en:", OUTPUT_PATH)

print("\nVista previa:")
cols_preview = [
    "confianza_limpieza", "confianza_fraude",
    "limpieza_num", "fraude_num", "fraude_rev",
    "confianza_idx", "confianza_idx_round", "confianza_3"
]
print(df_model[cols_preview].head())
