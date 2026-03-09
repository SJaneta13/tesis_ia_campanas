# src/03b_compare_models.py
# ============================================================================
# Consolidación y comparación de los 3 modelos de la tesis:
#   1. Random Forest
#   2. SVM-RBF
#   3. Regresión Logística Ordinal
#
# Métricas: accuracy, f1_weighted, f1_macro, kappa_qw, AUC, MAE, tiempo
# Ranking: f1_weighted → kappa_qw → accuracy (descendente)
# ============================================================================

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pathlib import Path


# =========================
# Locate latest run
# =========================
RUNS_DIR = Path("outputs") / "runs"
runs = sorted(RUNS_DIR.glob("run_*"))
if not runs:
    raise FileNotFoundError(
        "No hay runs en outputs/runs. Primero ejecuta src/03_modeling.py"
    )

RUN_DIR = runs[-1]
TABLES_DIR = RUN_DIR / "tables"
ORDINAL_DIR = RUN_DIR / "ordinal"
OUT_DIR = RUN_DIR / "tables"

print("Usando run:", RUN_DIR.name)


# =========================
# Helpers
# =========================
def find_latest_file(folder: Path, pattern: str) -> Path:
    files = sorted(folder.glob(pattern))
    if not files:
        raise FileNotFoundError(
            f"No se encontró ningún archivo con patrón {pattern} en {folder}"
        )
    return files[-1]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    return df


def safe_get(df, col, default=float("nan")):
    """Obtener columna si existe, sino valor por defecto."""
    return df[col] if col in df.columns else default


# =========================
# 1) Load sklearn summary metrics (run-level)
# =========================
sk_path = find_latest_file(TABLES_DIR, "metrics_run_*.csv")
df_sk = pd.read_csv(sk_path, encoding="utf-8-sig")
df_sk = normalize_columns(df_sk)

# Detectar target principal del run (desde sklearn)
if (df_sk["target"].astype(str) == "confianza_3").any():
    PRIMARY_TARGET = "confianza_3"
    PRIMARY_ORD = "ordinal_logit_3clases"
    PRIMARY_NC = 3
else:
    PRIMARY_TARGET = "confianza_idx_round"
    PRIMARY_ORD = "ordinal_logit_5niveles"
    PRIMARY_NC = 5

print("Target principal:", PRIMARY_TARGET, "| Ordinal:", PRIMARY_ORD)



df_sk_out = pd.DataFrame(
    {
        "run_id": df_sk["run_id"],
        "model": df_sk["model"],
        "variant": df_sk["target"],
        "n_classes": df_sk["target"].apply(
            lambda x: 3 if str(x) == "confianza_3" else 5
        ),
        "accuracy": df_sk["accuracy_mean"],
        "f1_weighted": df_sk["f1_weighted_mean"],
        "f1_macro": df_sk["f1_macro_mean"],
        "mae_ordinal": df_sk["mae_ordinal_mean"],
        "kappa_qw": df_sk["kappa_qw_mean"],
        "auc_ovr": safe_get(df_sk, "auc_ovr_mean"),
        "time_seconds": safe_get(df_sk, "time_seconds_mean"),
        "family": "sklearn",
        "notes": "mean over seeds (70/30 split, k=5 CV)",
    }
)

# =========================
# Filter sklearn metrics for primary target
# =========================

df_sk_out = df_sk_out[df_sk_out["variant"].astype(str) == PRIMARY_TARGET].copy()


# =========================
# 2) Load ordinal metrics (ahora con CV multi-seed)
# =========================
ord_path = ORDINAL_DIR / "metrics.csv"
if not ord_path.exists():
    raise FileNotFoundError(
        f"No existe {ord_path}. Ejecuta primero src/03a_ordinal_logit.py."
    )

df_ord = pd.read_csv(ord_path, encoding="utf-8-sig")
df_ord = normalize_columns(df_ord)

df_ord_out = pd.DataFrame(
    {
        "run_id": safe_get(df_ord, "run_id", RUN_DIR.name.replace("run_", "")),
        "model": "ordinal_logit",
        "variant": df_ord["target"],
        "n_classes": df_ord["n_classes"],
        "accuracy": safe_get(df_ord, "accuracy_mean", safe_get(df_ord, "accuracy")),
        "f1_weighted": safe_get(
            df_ord, "f1_weighted_mean", safe_get(df_ord, "f1_weighted")
        ),
        "f1_macro": safe_get(
            df_ord, "f1_macro_mean", safe_get(df_ord, "f1_macro")
        ),
        "mae_ordinal": safe_get(
            df_ord, "mae_ordinal_mean", safe_get(df_ord, "mae_ordinal")
        ),
        "kappa_qw": safe_get(
            df_ord, "kappa_qw_mean", safe_get(df_ord, "kappa_qw")
        ),
        "auc_ovr": safe_get(df_ord, "auc_ovr_mean"),
        "time_seconds": safe_get(df_ord, "time_seconds_mean"),
        "family": "statsmodels",
        "notes": safe_get(
            df_ord,
            "notes",
            "mean over seeds, CV selects logit/probit",
        ),
    }
)


df_ord_out = df_ord_out[df_ord_out["variant"].astype(str) == PRIMARY_ORD].copy()

# =========================
# 3) Combine and rank
# =========================
df_all = pd.concat([df_sk_out, df_ord_out], ignore_index=True)

# Ranking: f1_weighted → kappa_qw → accuracy (descendente)
df_all = df_all.sort_values(
    ["f1_weighted", "kappa_qw", "accuracy"], ascending=False
)

# Guardar tabla consolidada
out_csv = OUT_DIR / "metrics_compare_all_models.csv"
df_all.to_csv(out_csv, index=False, encoding="utf-8-sig")

print("\nTabla consolidada guardada en:", out_csv)
print("\nTop modelos (ordenado por f1_weighted, kappa_qw, accuracy):")
print(df_all.to_string(index=False))


# =========================
# 4) Best overall + resumen para tesis
# =========================
best = df_all.iloc[0].to_dict()

best_txt = OUT_DIR / "best_overall_model.txt"
best_txt.write_text(
    "Mejor modelo global (criterio: f1_weighted, luego kappa_qw, luego accuracy)\n"
    f"run: {RUN_DIR.name}\n"
    f"split: 70/30, CV: k=5, seeds: [0,7,13,21,42]\n\n"
    f"{best}\n",
    encoding="utf-8",
)

print("\nMejor modelo global:")
print(best)
print("Guardado en:", best_txt)


# =========================
# 5) Plot comparativo F1-weighted
# =========================
def short_label(row):
    if row["family"] == "sklearn":
        return f'{row["model"]} ({row["n_classes"]}c)'
    return f'ordinal_logit ({row["n_classes"]}c)'


df_plot = df_all.copy()
df_plot["label"] = df_plot.apply(short_label, axis=1)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Subplot 1: F1-weighted
axes[0].barh(df_plot["label"][::-1], df_plot["f1_weighted"][::-1])
axes[0].set_xlabel("F1-weighted")
axes[0].set_title("Comparación de modelos (F1-weighted)")

# Subplot 2: Kappa QW
axes[1].barh(df_plot["label"][::-1], df_plot["kappa_qw"][::-1], color="orange")
axes[1].set_xlabel("Kappa QW")
axes[1].set_title("Comparación de modelos (Kappa QW)")

plt.tight_layout()
plot_path = RUN_DIR / "figures" / "compare_models.png"
plt.savefig(plot_path, dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico guardado en:", plot_path)


# =========================
# 6) Plot AUC comparativo (si disponible)
# =========================
auc_vals = df_plot["auc_ovr"].dropna()
if len(auc_vals) > 0 and not all(np.isnan(v) for v in auc_vals):
    plt.figure(figsize=(9, 5))
    plt.barh(df_plot["label"][::-1], df_plot["auc_ovr"].fillna(0)[::-1], color="green")
    plt.xlabel("AUC (OvR weighted)")
    plt.title("Comparación de modelos (AUC)")
    plt.tight_layout()
    auc_path = RUN_DIR / "figures" / "compare_auc.png"
    plt.savefig(auc_path, dpi=150, bbox_inches="tight")
    plt.close()
    print("Gráfico AUC guardado en:", auc_path)


# =========================
# 7) Tabla resumen para tesis (formato LaTeX-friendly)
# =========================
thesis_cols = ["model", "n_classes", "accuracy", "f1_weighted", "kappa_qw", "auc_ovr", "time_seconds"]
existing_cols = [c for c in thesis_cols if c in df_all.columns]
df_thesis = df_all[existing_cols].copy()
df_thesis.to_csv(OUT_DIR / "tabla_resumen_tesis.csv", index=False, encoding="utf-8-sig")
print("\nTabla resumen tesis guardada en:", OUT_DIR / "tabla_resumen_tesis.csv")
