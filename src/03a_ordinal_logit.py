# src/03a_ordinal_logit.py
# ============================================================================
# Modelo Ordinal Logístico con Validación Cruzada (k=5, multi-seed)
#
# Según statsmodels docs (Context7): OrderedModel implementa Cumulative Link
# Models con distribuciones logit (logística acumulativa) y probit (CDF normal).
# Requiere hasconst=False cuando no se incluye intercepto explícito.
#
# Tesis: 70/30 split, k-fold=5, métricas: accuracy, AUC, f1, kappa, tiempo
# ============================================================================

import json
import time
import warnings
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Suprimir warnings (HessianInversion, convergence, etc.)
warnings.filterwarnings("ignore")

from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import label_binarize
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
)
from statsmodels.miscmodels.ordinal_model import OrderedModel

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*Maximum Likelihood optimization.*")


# =========================
# OUTPUTS: usar el último run de sklearn
# =========================
RUNS_DIR = Path("outputs") / "runs"
runs = sorted(RUNS_DIR.glob("run_*"))
if not runs:
    raise FileNotFoundError(
        "No hay runs en outputs/runs. Primero ejecuta src/03_modeling.py"
    )
last_run = runs[-1].name

OUT_DIR = RUNS_DIR / last_run / "ordinal"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIG_DIR = RUNS_DIR / last_run / "figures" / "ordinal"
FIG_DIR.mkdir(parents=True, exist_ok=True)

TABLES_DIR = RUNS_DIR / last_run / "tables"

print("Guardando ordinal en:", OUT_DIR)
print("Guardando figuras ordinal en:", FIG_DIR)


# =========================
# CONFIG (alineado con 03_modeling.py y tesis)
# =========================
INPUT_PATH = "data/processed/encuestas/model_ready.csv"

TARGET_5 = "confianza_idx_round"  # 1..5
TEST_SIZE = 0.30  # Tesis: 70% train / 30% validación
N_SPLITS = 5  # k-fold interno para comparación logit vs probit

# Mismas semillas que 03_modeling.py para comparación justa
SEEDS = [0, 7, 13, 21, 42]


# =========================
# Helpers (métricas ordinales)
# =========================
def mae_ordinal(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def quadratic_weighted_kappa(y_true, y_pred, min_rating, max_rating):
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    K = max_rating - min_rating + 1
    O = np.zeros((K, K), dtype=float)

    for a, p in zip(y_true, y_pred):
        O[a - min_rating, p - min_rating] += 1

    act_hist = np.bincount(y_true - min_rating, minlength=K).astype(float)
    pred_hist = np.bincount(y_pred - min_rating, minlength=K).astype(float)

    E = np.outer(act_hist, pred_hist)
    E = E / E.sum() * O.sum()

    W = np.zeros((K, K), dtype=float)
    for i in range(K):
        for j in range(K):
            W[i, j] = ((i - j) ** 2) / ((K - 1) ** 2)

    num = (W * O).sum()
    den = (W * E).sum()
    return float(1 - (num / den if den != 0 else 0))


def compute_auc_ovr(y_true, y_proba, n_classes):
    """AUC One-vs-Rest para clasificación multiclase ordinal."""
    try:
        y_bin = label_binarize(y_true, classes=list(range(1, n_classes + 1)))
        if y_bin.shape[1] == 1:
            return float(roc_auc_score(y_bin, y_proba[:, :1]))
        return float(
            roc_auc_score(y_bin, y_proba, multi_class="ovr", average="weighted")
        )
    except Exception:
        return float("nan")


def eval_metrics(y_true, y_pred, y_proba, n_classes):
    acc = accuracy_score(y_true, y_pred)
    f1w = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    f1m = f1_score(y_true, y_pred, average="macro", zero_division=0)
    mae = mae_ordinal(y_true, y_pred)
    qwk = quadratic_weighted_kappa(
        y_true, y_pred, min_rating=1, max_rating=n_classes
    )
    auc = compute_auc_ovr(y_true, y_proba, n_classes)
    return {
        "accuracy": float(acc),
        "f1_weighted": float(f1w),
        "f1_macro": float(f1m),
        "mae_ordinal": float(mae),
        "kappa_qw": float(qwk),
        "auc_ovr": auc,
    }


def to_3_classes(x):
    if x <= 2:
        return 1
    elif x == 3:
        return 2
    else:
        return 3


# =========================
# Feature building
# =========================
def build_x_y(df, target_col):
    DROP_COLS = [
        "confianza_idx",
        "confianza_idx_round",
        "limpieza_num",
        "fraude_num",
        "fraude_rev",
        "confianza_limpieza",
        "confianza_fraude",
        "Marca temporal",
        "confianza_3",
    ]

    TEXT_COL = (
        "¿Qué recomendaciones haría para garantizar un uso responsable y "
        "transparente de la inteligencia artificial en campañas políticas "
        "digitales en Ecuador, considerando la experiencia de la campaña "
        "entre Luisa González y Daniel Noboa?"
    )
    if TEXT_COL in df.columns:
        DROP_COLS.append(TEXT_COL)

    X = df.drop(
        columns=[c for c in DROP_COLS if c in df.columns], errors="ignore"
    ).copy()
    y = df[target_col].astype(int).copy()

    # Variables independientes según tesis:
    # Conocimiento sobre IA, frecuencia de exposición, edad, género, facultad, rol
    base_keep = [
        "edad",
        "genero",
        "rol_uce",
        "conoce_ia",
        "percibe_automatizacion",
        "identifica_ia",
        "¿Ha cambiado su confianza en el proceso electoral al saber que "
        "existen bots, deepfakes o manipulación mediante IA?",
        "¿Considera que el uso de IA en campañas digitales influyó en su "
        "decisión de voto en las elecciones presidenciales de 2025?",
        "¿Realiza alguna verificación (chequea fuentes, busca noticias, "
        "consulta otras personas) de la información política digital antes "
        "de compartirla?",
        "¿Conoce alguna medida, ley o regulación sobre el uso de IA en "
        "campañas políticas en Ecuador?",
        "¿Cree que debería regularse el uso de IA en campañas políticas "
        "digitales en el país?",
    ]

    likert_num_cols = [
        c for c in X.columns if isinstance(c, str) and c.endswith("_num")
    ]
    keep_cols = [c for c in base_keep if c in X.columns] + likert_num_cols
    X = X[keep_cols].copy()

    # One-hot encoding
    x_enc = pd.get_dummies(X, drop_first=True)

    # Limpieza numérica
    x_enc = x_enc.replace([np.inf, -np.inf], np.nan)
    med = x_enc.median(numeric_only=True)
    x_enc = x_enc.fillna(med).fillna(0)
    x_enc = x_enc.apply(pd.to_numeric, errors="coerce").fillna(0.0).astype(float)

    if "const" in x_enc.columns:
        x_enc = x_enc.drop(columns=["const"])

    # Quitar columnas constantes o varianza 0
    nunique = x_enc.nunique(dropna=False)
    const_cols = nunique[nunique <= 1].index.tolist()
    var0_cols = x_enc.columns[(x_enc.var(axis=0) == 0)].tolist()
    drop_cols = sorted(set(const_cols + var0_cols))
    if drop_cols:
        x_enc = x_enc.drop(columns=drop_cols)

    if x_enc.shape[1] == 0:
        raise ValueError("x_enc quedó sin columnas después de limpieza.")

    return x_enc, y


# =========================
# Plot helpers
# =========================
def save_cm_png(cm, n_classes, tag):
    plt.figure(figsize=(5, 4))
    plt.imshow(cm)
    plt.title(f"Matriz de confusión - {tag}")
    plt.xlabel("Predicción")
    plt.ylabel("Real")
    plt.xticks(range(n_classes), range(1, n_classes + 1))
    plt.yticks(range(n_classes), range(1, n_classes + 1))
    for i in range(n_classes):
        for j in range(n_classes):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center")
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"cm_{tag}.png", dpi=150)
    plt.close()


def save_or_png(coef_df, tag, top_n=10):
    plot_df = coef_df[
        ~coef_df["term"].str.contains(r"^\d+/\d+$", regex=True)
    ].copy()
    plot_df["abs_coef"] = plot_df["coef"].abs()
    top = plot_df.sort_values("abs_coef", ascending=False).head(top_n)
    ypos = np.arange(len(top))
    plt.figure(figsize=(9, 5))
    plt.errorbar(
        top["odds_ratio"],
        ypos,
        xerr=[
            top["odds_ratio"] - top["or_ci_low"],
            top["or_ci_high"] - top["odds_ratio"],
        ],
        fmt="o",
    )
    plt.axvline(1.0, linestyle="--")
    plt.yticks(ypos, top["term"])
    plt.xlabel("Odds Ratio (OR)")
    plt.title(f"Top {top_n} OR (IC 95%) - {tag}")
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"or_top_{tag}.png", dpi=150)
    plt.close()


# =========================
# Load data
# =========================
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig").copy()
df = df.dropna(subset=[TARGET_5]).copy()
df[TARGET_5] = df[TARGET_5].astype(int)
df["confianza_3"] = df[TARGET_5].apply(to_3_classes).astype(int)

print(f"Dataset para ordinal: {df.shape}")
print(f"Distribución target 5: {df[TARGET_5].value_counts().sort_index().to_dict()}")
print(
    f"Distribución target 3: {df['confianza_3'].value_counts().sort_index().to_dict()}"
)


# =========================
# ORDINAL FIT con CV interno (logit vs probit)
# =========================
def fit_ordinal_single(X_train, y_train, X_test, distr="logit"):
    """Entrena OrderedModel y predice. Retorna (y_pred, proba, res)."""
    model = OrderedModel(
        y_train.values, X_train.values, distr=distr, hasconst=False
    )
    res = model.fit(method="lbfgs", disp=False, maxiter=500)
    proba = res.model.predict(res.params, exog=X_test.values)
    y_pred = np.asarray(np.argmax(proba, axis=1) + 1, dtype=int)
    return y_pred, proba, res


def cv_select_distribution(X_train, y_train, n_classes, seed):
    """Validación cruzada k=5 interna para seleccionar logit vs probit."""
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=seed)
    cv_scores = {"logit": [], "probit": []}

    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
        X_tr = X_train.iloc[train_idx]
        y_tr = y_train.iloc[train_idx]
        X_val = X_train.iloc[val_idx]
        y_val = y_train.iloc[val_idx]

        # Quitar columnas varianza 0 del fold
        zero_var = X_tr.columns[(X_tr.var(axis=0) == 0)].tolist()
        if zero_var:
            X_tr = X_tr.drop(columns=zero_var)
            X_val = X_val.drop(columns=zero_var, errors="ignore")
        X_val = X_val.reindex(columns=X_tr.columns, fill_value=0.0)

        for distr in ["logit", "probit"]:
            try:
                y_pred, _, _ = fit_ordinal_single(X_tr, y_tr, X_val, distr=distr)
                f1 = f1_score(y_val, y_pred, average="weighted", zero_division=0)
                cv_scores[distr].append(f1)
            except Exception:
                cv_scores[distr].append(0.0)

    mean_logit = np.mean(cv_scores["logit"])
    mean_probit = np.mean(cv_scores["probit"])

    best_distr = "logit" if mean_logit >= mean_probit else "probit"

    return best_distr, {
        "cv_f1_logit_mean": float(mean_logit),
        "cv_f1_logit_std": float(np.std(cv_scores["logit"])),
        "cv_f1_probit_mean": float(mean_probit),
        "cv_f1_probit_std": float(np.std(cv_scores["probit"])),
    }


# =========================
# MAIN LOOP: Multi-seed (igual que 03_modeling.py)
# =========================
rows_seed_level = []
all_summaries = []


def run_ordinal_multi_seed(target_col, n_classes, tag):
    print(f"\n{'='*50}")
    print(f"Ordinal Logit/Probit - {tag} ({n_classes} clases)")
    print(f"{'='*50}")

    X_enc, y = build_x_y(df, target_col)
    per_seed_metrics = []

    for seed in SEEDS:
        print(f"\n  Seed {seed}:")
        t_start = time.perf_counter()

        # Split 70/30 estratificado (mismo que sklearn models)
        X_train, X_test, y_train, y_test = train_test_split(
            X_enc, y, test_size=TEST_SIZE, random_state=seed, stratify=y
        )

        # Quitar columnas varianza 0 del TRAIN y alinear TEST
        zero_var = X_train.columns[(X_train.var(axis=0) == 0)].tolist()
        if zero_var:
            X_train = X_train.drop(columns=zero_var)
            X_test = X_test.drop(columns=zero_var, errors="ignore")
        X_test = X_test.reindex(columns=X_train.columns, fill_value=0.0)

        # CV interno: seleccionar mejor distribución (logit vs probit)
        best_distr, cv_info = cv_select_distribution(
            X_train, y_train, n_classes, seed
        )
        print(
            f"    CV interno: logit={cv_info['cv_f1_logit_mean']:.3f}, "
            f"probit={cv_info['cv_f1_probit_mean']:.3f} -> "
            f"{best_distr}"
        )

        # Entrenar modelo final en TODO el train, evaluar en test
        y_pred, y_proba, res = fit_ordinal_single(
            X_train, y_train, X_test, distr=best_distr
        )

        t_elapsed = time.perf_counter() - t_start

        # Métricas
        mets = eval_metrics(y_test, y_pred, y_proba, n_classes=n_classes)
        mets["time_seconds"] = round(t_elapsed, 2)
        per_seed_metrics.append(mets)

        print(
            f"    Test: acc={mets['accuracy']:.3f}, f1w={mets['f1_weighted']:.3f}, "
            f"kappa={mets['kappa_qw']:.3f}, auc={mets['auc_ovr']:.3f}, "
            f"time={t_elapsed:.1f}s"
        )

        # Guardar por seed
        rows_seed_level.append(
            {
                "run_id": last_run.replace("run_", ""),
                "model": "ordinal_logit",
                "seed": seed,
                "target": tag,
                "n_classes": n_classes,
                "distribution": best_distr,
                "n_train": int(len(y_train)),
                "n_test": int(len(y_test)),
                **mets,
                **cv_info,
            }
        )

        # Guardar artefactos SOLO para primer seed
        if seed == SEEDS[0]:
            cm = confusion_matrix(
                y_test, y_pred, labels=list(range(1, n_classes + 1))
            )
            pd.DataFrame(cm).to_csv(
                OUT_DIR / f"confusion_matrix_{tag}.csv",
                index=False,
                encoding="utf-8-sig",
            )
            save_cm_png(cm, n_classes=n_classes, tag=tag)

            report = classification_report(y_test, y_pred, zero_division=0)
            (OUT_DIR / f"report_{tag}.txt").write_text(report, encoding="utf-8")

            try:
                (OUT_DIR / f"summary_{tag}.txt").write_text(
                    res.summary().as_text(), encoding="utf-8"
                )
            except Exception:
                (OUT_DIR / f"summary_{tag}.txt").write_text(
                    f"Summary unavailable (Hessian inversion failed)\nParams: {params}",
                    encoding="utf-8",
                )

            params = res.params
            try:
                conf = res.conf_int()
            except Exception:
                conf = None

            # params puede ser ndarray si Hessian falla; manejar ambos casos
            if hasattr(params, 'index'):
                term_names = params.index.tolist()
                param_vals = params.values
            else:
                term_names = [f"x{i}" for i in range(len(params))]
                param_vals = np.asarray(params)

            coef_dict = {
                "term": term_names,
                "coef": param_vals,
                "odds_ratio": np.exp(param_vals),
            }
            if conf is not None:
                if hasattr(conf, 'values'):
                    coef_dict["ci_low"] = conf.iloc[:, 0].values
                    coef_dict["ci_high"] = conf.iloc[:, 1].values
                else:
                    coef_dict["ci_low"] = conf[:, 0]
                    coef_dict["ci_high"] = conf[:, 1]
                coef_dict["or_ci_low"] = np.exp(coef_dict["ci_low"])
                coef_dict["or_ci_high"] = np.exp(coef_dict["ci_high"])

            coef_df = pd.DataFrame(coef_dict)
            coef_df.to_csv(
                OUT_DIR / f"coefficients_{tag}.csv",
                index=False,
                encoding="utf-8-sig",
            )
            save_or_png(coef_df, tag=tag, top_n=10)

            pred_df = pd.DataFrame({"y_true": y_test.values, "y_pred": y_pred})
            pred_df.to_csv(
                OUT_DIR / f"predictions_{tag}.csv",
                index=False,
                encoding="utf-8-sig",
            )

    # Agregar resumen (promedio + std sobre seeds)
    metric_keys = [
        "accuracy",
        "f1_weighted",
        "f1_macro",
        "mae_ordinal",
        "kappa_qw",
        "auc_ovr",
        "time_seconds",
    ]
    agg = {}
    for k in metric_keys:
        vals = [d[k] for d in per_seed_metrics]
        clean = [v for v in vals if not np.isnan(v)]
        agg[f"{k}_mean"] = float(np.mean(clean)) if clean else float("nan")
        agg[f"{k}_std"] = float(np.std(clean, ddof=0)) if clean else float("nan")

    summary_row = {
        "run_id": last_run.replace("run_", ""),
        "model": "ordinal_logit",
        "target": tag,
        "n_classes": n_classes,
        "n_total": int(len(df)),
        "n_features": int(X_enc.shape[1]),
        "seeds": json.dumps(SEEDS),
        "test_size": TEST_SIZE,
        "n_splits_cv": N_SPLITS,
        **agg,
        "notes": f"mean over {len(SEEDS)} seeds, CV selects logit/probit",
    }

    print(
        f"\n  Resumen {tag}: "
        f"f1w={agg['f1_weighted_mean']:.3f} +/- {agg['f1_weighted_std']:.3f}, "
        f"kappa={agg['kappa_qw_mean']:.3f}, auc={agg['auc_ovr_mean']:.3f}"
    )

    return summary_row


# =========================
# Ejecutar para 3 y 5 clases
# =========================
summary_3c = run_ordinal_multi_seed(
    "confianza_3", n_classes=3, tag="ordinal_logit_3clases"
)
summary_5c = run_ordinal_multi_seed(
    TARGET_5, n_classes=5, tag="ordinal_logit_5niveles"
)

all_summaries = [summary_3c, summary_5c]


# =========================
# Save metrics (formato compatible con 03_modeling.py)
# =========================
df_seed = pd.DataFrame(rows_seed_level)
df_seed.to_csv(OUT_DIR / "metrics_by_seed.csv", index=False, encoding="utf-8-sig")

df_run = pd.DataFrame(all_summaries)
df_run.to_csv(OUT_DIR / "metrics.csv", index=False, encoding="utf-8-sig")

(OUT_DIR / "metrics.json").write_text(
    df_run.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8"
)

print("\n" + "=" * 50)
print("Ordinal completado.")
print(f"  Metricas resumen: {OUT_DIR / 'metrics.csv'}")
print(f"  Metricas por seed: {OUT_DIR / 'metrics_by_seed.csv'}")
print(f"  Figuras: {FIG_DIR}")
print("=" * 50)
