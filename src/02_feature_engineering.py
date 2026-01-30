import pandas as pd
import numpy as np
from pathlib import Path

# RUTAS (encuestas)
# ==========
INPUT_PATH = Path("data/processed/encuestas/respuestas_limpias.csv")
OUTPUT_DIR = Path("data/processed/encuestas")
OUTPUT_PATH = OUTPUT_DIR / "model_ready.csv"


# Crear carpeta de salida si no existe
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
    "Totalmente de acuerdo": 5
}

# Validación temprana para evitar KeyError silencioso
required = ["confianza_limpieza", "confianza_fraude"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise KeyError(f"Faltan columnas requeridas: {missing}. Columnas actuales: {df.columns.tolist()}")

df["limpieza_num"] = (
    df["confianza_limpieza"].astype(str).str.strip().map(likert_map)
)

df["fraude_num"] = (
    df["confianza_fraude"].astype(str).str.strip().map(likert_map)
)

df["fraude_rev"] = 6 - df["fraude_num"]

df["confianza_idx"] = (df["limpieza_num"] + df["fraude_rev"]) / 2
df["confianza_idx_round"] = df["confianza_idx"].round().astype("Int64")

mask_invalid = df[["limpieza_num", "fraude_num"]].isna().any(axis=1)
print("Filas con valores no válidos en limpieza_num o fraude_num:", int(mask_invalid.sum()))

if mask_invalid.any():
    print("\nEjemplos de filas problemáticas (texto original):")
    print(df.loc[mask_invalid, ["confianza_limpieza", "confianza_fraude"]].head(20))

# ============================
# Features Likert (Percepción IA) -> numéricas
# ============================
likert_cols = [c for c in df.columns if c.startswith("Percepción sobre el uso de IA en campañas políticas")]

for c in likert_cols:
    df[c + "_num"] = (
        df[c].astype(str).str.strip().map(likert_map)
    )

# ============================
# Creacion del Modelo 
#  ============================

df_model = df.dropna(subset=["confianza_idx"]).copy()


num_created = [c for c in df_model.columns if c.endswith("_num")]
print("Nuevas columnas numéricas (_num):", len(num_created))
print("Ejemplo:", num_created[:5])





print("Filas válidas para modelado:", df_model.shape[0])

df_model.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print("Archivo guardado en:", OUTPUT_PATH)

print("\nVista previa:")
print(df_model[["confianza_limpieza", "confianza_fraude", "limpieza_num", "fraude_num", "fraude_rev", "confianza_idx"]].head())


