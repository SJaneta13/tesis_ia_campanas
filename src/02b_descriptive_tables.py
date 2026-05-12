import pandas as pd
import re
from pathlib import Path

INPUT_PATH = Path("data/processed/encuestas/respuestas_limpias.csv")
MODEL_PATH = Path("data/processed/encuestas/model_ready.csv")
OUT_DIR = Path("outputs/descriptive")
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
df_model = pd.read_csv(MODEL_PATH, encoding="utf-8-sig")


def clean_filename(text, max_len=80):
    text = str(text).lower()
    text = text.replace("¿", "").replace("?", "")
    text = text.replace("á", "a").replace("é", "e").replace("í", "i")
    text = text.replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text[:max_len]


def save_freq_table(df_in, col, out_name):
    if col not in df_in.columns:
        print(f"[WARN] No existe columna: {col}")
        return

    tab = (
        df_in[col]
        .fillna("No responde")
        .astype(str)
        .str.strip()
        .value_counts(dropna=False)
        .rename_axis("categoria")
        .reset_index(name="n")
    )

    tab["porcentaje"] = (tab["n"] / tab["n"].sum() * 100).round(2)

    tab.to_csv(OUT_DIR / out_name, index=False, encoding="utf-8-sig")
    print("Guardado:", out_name)


def save_crosstab(df_in, row_var, col_var, out_name):
    if row_var not in df_in.columns or col_var not in df_in.columns:
        print(f"[WARN] No existe {row_var} o {col_var}")
        return

    ct = pd.crosstab(df_in[row_var], df_in[col_var], margins=True)
    ct.to_csv(OUT_DIR / out_name, encoding="utf-8-sig")
    print("Guardado:", out_name)


def save_crosstab_pct(df_in, row_var, col_var, out_name):
    if row_var not in df_in.columns or col_var not in df_in.columns:
        print(f"[WARN] No existe {row_var} o {col_var}")
        return

    ct = pd.crosstab(df_in[row_var], df_in[col_var], normalize="index") * 100
    ct = ct.round(2)
    ct.to_csv(OUT_DIR / out_name, encoding="utf-8-sig")
    print("Guardado:", out_name)


# ============================
# Tablas descriptivas básicas
# ============================

basic_cols = {
    "edad": "tabla_edad.csv",
    "genero": "tabla_genero.csv",
    "rol_uce": "tabla_rol_uce.csv",
    "conoce_ia": "tabla_conoce_ia.csv",
    "percibe_automatizacion": "tabla_percibe_automatizacion.csv",
    "identifica_ia": "tabla_identifica_ia.csv",
}

for col, out_name in basic_cols.items():
    save_freq_table(df, col, out_name)


# ============================
# Distribución de confianza electoral
# ============================

save_freq_table(df_model, "confianza_idx_round", "tabla_confianza_5niveles.csv")
save_freq_table(df_model, "confianza_3", "tabla_confianza_3clases.csv")


# ============================
# Variables temáticas relevantes
# ============================

extra_cols = [
    "¿Con qué frecuencia vio contenido político digital durante la campaña presidencial de 2025?",
    "¿Ha cambiado su confianza en el proceso electoral al saber que existen bots, deepfakes o manipulación mediante IA?",
    "¿Considera que el uso de IA en campañas digitales influyó en su decisión de voto en las elecciones presidenciales de 2025?",
    "¿Realiza alguna verificación (chequea fuentes, busca noticias, consulta otras personas) de la información política digital antes de compartirla?",
    "¿Conoce alguna medida, ley o regulación sobre el uso de IA en campañas políticas en Ecuador?",
    "¿Cree que debería regularse el uso de IA en campañas políticas digitales en el país?",
]

for col in extra_cols:
    out_name = f"tabla_{clean_filename(col)}.csv"
    save_freq_table(df, col, out_name)


# ============================
# Cruces con confianza electoral
# ============================

cross_vars = [
    "edad",
    "genero",
    "rol_uce",
    "conoce_ia",
    "percibe_automatizacion",
    "identifica_ia",
]

for var in cross_vars:
    save_crosstab(
        df_model,
        var,
        "confianza_idx_round",
        f"{clean_filename(var)}_vs_confianza_5niveles.csv"
    )

    save_crosstab(
        df_model,
        var,
        "confianza_3",
        f"{clean_filename(var)}_vs_confianza_3clases.csv"
    )

    save_crosstab_pct(
        df_model,
        var,
        "confianza_3",
        f"{clean_filename(var)}_vs_confianza_3clases_pct.csv"
    )


# ============================
# Resumen descriptivo para tesis
# ============================

resumen = pd.DataFrame([{
    "archivo_fuente": str(INPUT_PATH),
    "archivo_modelado": str(MODEL_PATH),
    "filas_respuestas_limpias": int(df.shape[0]),
    "filas_model_ready": int(df_model.shape[0]),
    "columnas_respuestas_limpias": int(df.shape[1]),
    "columnas_model_ready": int(df_model.shape[1]),
    "salida": str(OUT_DIR),
    "nota": "Tablas descriptivas y cruces generados para el Capítulo 4 y anexos."
}])

resumen.to_csv(
    OUT_DIR / "resumen_tablas_descriptivas.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nTablas descriptivas generadas correctamente.")