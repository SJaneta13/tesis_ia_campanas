# src/03b_compare_models.py
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# =========================
# Locate latest run
# =========================
RUNS_DIR = Path("outputs") / "runs"
runs = sorted(RUNS_DIR.glob("run_*"))
if not runs:
    raise FileNotFoundError("No hay runs en outputs/runs. Primero ejecuta src/03_modeling.py")

RUN_DIR = runs[-1]
TABLES_DIR = RUN_DIR / "tables"
ORDINAL_DIR = RUN_DIR / "ordinal"
OUT_DIR = RUN_DIR / "tables"  # consolidamos en tables (misma corrida)

print("Usando run:", RUN_DIR.name)


# =========================
# Helpers
# =========================
def find_latest_file(folder: Path, pattern: str) -> Path:
    files = sorted(folder.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No se encontró ningún archivo con patrón {pattern} en {folder}")
    # normalmente hay 1 por run, pero si hubiera varios, agarra el último
    return files[-1]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    return df


def add_model_family(df: pd.DataFrame, family: str) -> pd.DataFrame:
    df = df.copy()
    df["family"] = family
    return df


# =========================
# 1) Load sklearn summary metrics (run-level)
# =========================
sk_path = find_latest_file(TABLES_DIR, "metrics_run_*.csv")
df_sk = pd.read_csv(sk_path, encoding="utf-8-sig")
df_sk = normalize_columns(df_sk)

# Estandarizar a esquema comparable:
# df_sk tiene columnas: model, target, accuracy_mean, f1_weighted_mean, etc.
df_sk_out = pd.DataFrame({
    "run_id": df_sk["run_id"],
    "model": df_sk["model"],
    "variant": df_sk["target"],  # ej: confianza_3 o confianza_idx_round
    "n_classes": df_sk["target"].apply(lambda x: 3 if str(x) == "confianza_3" else 5),
    "accuracy": df_sk["accuracy_mean"],
    "f1_weighted": df_sk["f1_weighted_mean"],
    "f1_macro": df_sk["f1_macro_mean"],
    "mae_ordinal": df_sk["mae_ordinal_mean"],
    "kappa_qw": df_sk["kappa_qw_mean"],
    "notes": "mean over seeds"
})
df_sk_out = add_model_family(df_sk_out, "sklearn")


# =========================
# 2) Load ordinal metrics
# =========================
ord_path = ORDINAL_DIR / "metrics.csv"
if not ord_path.exists():
    raise FileNotFoundError(
        f"No existe {ord_path}. Ejecuta primero src/03a_ordinal_logit.py para esta corrida."
    )

df_ord = pd.read_csv(ord_path, encoding="utf-8-sig")
df_ord = normalize_columns(df_ord)

# df_ord ya viene con: target, n_classes, accuracy, f1_weighted, f1_macro, mae_ordinal, kappa_qw
df_ord_out = pd.DataFrame({
    "run_id": RUN_DIR.name.replace("run_", ""),
    "model": "ordinal_logit",
    "variant": df_ord["target"],  # ordinal_logit_3clases / ordinal_logit_5niveles
    "n_classes": df_ord["n_classes"],
    "accuracy": df_ord["accuracy"],
    "f1_weighted": df_ord["f1_weighted"],
    "f1_macro": df_ord["f1_macro"],
    "mae_ordinal": df_ord["mae_ordinal"],
    "kappa_qw": df_ord["kappa_qw"],
    "notes": "single split (seed=42)"
})
df_ord_out = add_model_family(df_ord_out, "statsmodels")


# =========================
# 3) Combine and rank
# =========================
df_all = pd.concat([df_sk_out, df_ord_out], ignore_index=True)

# Ranking prudente: principal f1_weighted (robustez en clases desbalanceadas)
df_all = df_all.sort_values(["f1_weighted", "kappa_qw", "accuracy"], ascending=False)

# Guardar tabla consolidada
out_csv = OUT_DIR / "metrics_compare_all_models.csv"
df_all.to_csv(out_csv, index=False, encoding="utf-8-sig")

print("\nTabla consolidada guardada en:", out_csv)
print("\nTop 10 (ordenado por f1_weighted, kappa_qw, accuracy):")
print(df_all.head(10))


# =========================
# 4) Best overall + resumen para tesis
# =========================
best = df_all.iloc[0].to_dict()

best_txt = OUT_DIR / "best_overall_model.txt"
best_txt.write_text(
    "Mejor modelo global (criterio: f1_weighted, luego kappa_qw, luego accuracy)\n"
    f"run: {RUN_DIR.name}\n\n"
    f"{best}\n",
    encoding="utf-8"
)

print("\nMejor modelo global:")
print(best)
print("Guardado en:", best_txt)


# =========================
# 5) Plot comparativo (opcional)
# =========================
# Para que el gráfico quede legible: etiqueta corta
def short_label(row):
    if row["family"] == "sklearn":
        return f'{row["model"]} ({row["n_classes"]}c)'
    return f'ordinal_logit ({row["n_classes"]}c)'

df_plot = df_all.copy()
df_plot["label"] = df_plot.apply(short_label, axis=1)

plt.figure(figsize=(9, 5))
plt.bar(df_plot["label"], df_plot["f1_weighted"])
plt.xticks(rotation=30, ha="right")
plt.ylabel("F1-weighted")
plt.title("Comparación de modelos (F1-weighted)")
plt.tight_layout()

plot_path = (RUN_DIR / "figures" / "compare_f1_weighted.png")
plt.savefig(plot_path, dpi=150)
plt.close()

print("Gráfico guardado en:", plot_path)
