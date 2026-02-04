# src/03a_ordinal_logit.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from statsmodels.miscmodels.ordinal_model import OrderedModel


# =========================
# OUTPUTS: usar el último run de sklearn
# =========================
RUNS_DIR = Path("outputs") / "runs"
runs = sorted(RUNS_DIR.glob("run_*"))
if not runs:
    raise FileNotFoundError("No hay runs en outputs/runs. Primero ejecuta src/03_modeling.py")
last_run = runs[-1].name


OUT_DIR = RUNS_DIR / last_run / "ordinal"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIG_DIR = OUT_DIR.parent / "figures" / "ordinal"
FIG_DIR.mkdir(parents=True, exist_ok=True)

print("Guardando ordinal en:", OUT_DIR)
print("Guardando figuras ordinal en:", FIG_DIR)


# =========================
# CONFIG
# =========================
INPUT_PATH = "data/processed/encuestas/model_ready.csv"

TARGET_5 = "confianza_idx_round"   # 1..5
TEST_SIZE = 0.20
SEED = 42


# =========================
# Helpers (ordinal metrics)
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


def eval_metrics(y_true, y_pred, n_classes):
    acc = accuracy_score(y_true, y_pred)
    f1w = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    f1m = f1_score(y_true, y_pred, average="macro", zero_division=0)
    mae = mae_ordinal(y_true, y_pred)
    qwk = quadratic_weighted_kappa(y_true, y_pred, min_rating=1, max_rating=n_classes)
    return {
        "accuracy": float(acc),
        "f1_weighted": float(f1w),
        "f1_macro": float(f1m),
        "mae_ordinal": float(mae),
        "kappa_qw": float(qwk)
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
        "confianza_idx", "confianza_idx_round",
        "limpieza_num", "fraude_num", "fraude_rev",
        "confianza_limpieza", "confianza_fraude",
        "Marca temporal",
        "confianza_3"
    ]

    TEXT_COL = "¿Qué recomendaciones haría para garantizar un uso responsable y transparente de la inteligencia artificial en campañas políticas digitales en Ecuador, considerando la experiencia de la campaña entre Luisa González y Daniel Noboa?"
    if TEXT_COL in df.columns:
        DROP_COLS.append(TEXT_COL)

    X = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors="ignore").copy()
    y = df[target_col].astype(int).copy()

    # Selección prudente de predictores
    base_keep = [
        "edad", "genero", "rol_uce",
        "conoce_ia", "percibe_automatizacion", "identifica_ia",
        "¿Ha cambiado su confianza en el proceso electoral al saber que existen bots, deepfakes o manipulación mediante IA?",
        "¿Considera que el uso de IA en campañas digitales influyó en su decisión de voto en las elecciones presidenciales de 2025?",
        "¿Realiza alguna verificación (chequea fuentes, busca noticias, consulta otras personas) de la información política digital antes de compartirla?",
        "¿Conoce alguna medida, ley o regulación sobre el uso de IA en campañas políticas en Ecuador?",
        "¿Cree que debería regularse el uso de IA en campañas políticas digitales en el país?"
    ]

    likert_num_cols = [c for c in X.columns if isinstance(c, str) and c.endswith("_num")]
    keep_cols = [c for c in base_keep if c in X.columns] + likert_num_cols
    X = X[keep_cols].copy()

    # One-hot
    x_enc = pd.get_dummies(X, drop_first=True)

    # Limpieza numérica
    x_enc = x_enc.replace([np.inf, -np.inf], np.nan)
    med = x_enc.median(numeric_only=True)
    x_enc = x_enc.fillna(med).fillna(0)
    x_enc = x_enc.apply(pd.to_numeric, errors="coerce").fillna(0.0).astype(float)

    # Borrar const si existiera
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
        raise ValueError("x_enc quedó sin columnas después de limpieza (constantes/varianza 0). Revisa features.")

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
    # excluir thresholds tipo 1/2, 2/3...
    plot_df = coef_df[~coef_df["term"].str.contains(r"^\d+/\d+$", regex=True)].copy()

    # ordenar por |coef|
    plot_df["abs_coef"] = plot_df["coef"].abs()
    top = plot_df.sort_values("abs_coef", ascending=False).head(top_n)

    ypos = np.arange(len(top))
    plt.figure(figsize=(9, 5))
    plt.errorbar(
        top["odds_ratio"],
        ypos,
        xerr=[
            top["odds_ratio"] - top["or_ci_low"],
            top["or_ci_high"] - top["odds_ratio"]
        ],
        fmt="o"
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


# =========================
# Train/evaluate
# =========================
results = []


def fit_and_eval(target_col, n_classes, tag):
    X_enc, y = build_x_y(df, target_col)

    X_train, X_test, y_train, y_test = train_test_split(
        X_enc, y, test_size=TEST_SIZE, random_state=SEED, stratify=y
    )

    # quitar columnas varianza 0 del TRAIN y alinear TEST
    zero_var = X_train.columns[(X_train.var(axis=0) == 0)].tolist()
    if zero_var:
        X_train = X_train.drop(columns=zero_var)
        X_test = X_test.drop(columns=zero_var, errors="ignore")

    X_test = X_test.reindex(columns=X_train.columns, fill_value=0.0)

    # ------------------------------------------------------------------
    # Modelo ordinal con distribución LOGIT (estándar)
    # Según statsmodels docs: distr='logit' usa función logística acumulativa
    # ------------------------------------------------------------------
    model_logit = OrderedModel(y_train, X_train, distr="logit", hasconst=False)
    res_logit = model_logit.fit(method="lbfgs", disp=False, maxiter=300)

    proba_logit = res_logit.model.predict(res_logit.params, exog=X_test)
    y_pred_logit = np.asarray(np.argmax(proba_logit, axis=1) + 1, dtype=int)
    mets_logit = eval_metrics(y_test, y_pred_logit, n_classes=n_classes)

    # ------------------------------------------------------------------
    # Modelo ordinal con distribución PROBIT (alternativa)
    # Según statsmodels docs: distr='probit' usa CDF normal (más colas ligeras)
    # ------------------------------------------------------------------
    model_probit = OrderedModel(y_train, X_train, distr="probit", hasconst=False)
    res_probit = model_probit.fit(method="lbfgs", disp=False, maxiter=300)

    proba_probit = res_probit.model.predict(res_probit.params, exog=X_test)
    y_pred_probit = np.asarray(np.argmax(proba_probit, axis=1) + 1, dtype=int)
    mets_probit = eval_metrics(y_test, y_pred_probit, n_classes=n_classes)

    # Seleccionar mejor modelo por F1-weighted
    if mets_logit["f1_weighted"] >= mets_probit["f1_weighted"]:
        res = res_logit
        y_pred = y_pred_logit
        mets = mets_logit
        best_distr = "logit"
    else:
        res = res_probit
        y_pred = y_pred_probit
        mets = mets_probit
        best_distr = "probit"

    print(f"  > {tag}: logit F1={mets_logit['f1_weighted']:.3f}, probit F1={mets_probit['f1_weighted']:.3f} -> MEJOR: {best_distr}")

    # artefactos
    (OUT_DIR / f"summary_{tag}.txt").write_text(res.summary().as_text(), encoding="utf-8")

    params = res.params
    conf = res.conf_int()

    coef_df = pd.DataFrame({
        "term": params.index,
        "coef": params.values,
        "odds_ratio": np.exp(params.values),
        "ci_low": conf[0].values,
        "ci_high": conf[1].values,
        "or_ci_low": np.exp(conf[0].values),
        "or_ci_high": np.exp(conf[1].values),
    })
    coef_df.to_csv(OUT_DIR / f"coefficients_{tag}.csv", index=False, encoding="utf-8-sig")

    pred_df = pd.DataFrame({"y_true": y_test.values, "y_pred": y_pred})
    pred_df.to_csv(OUT_DIR / f"predictions_{tag}.csv", index=False, encoding="utf-8-sig")

    cm = confusion_matrix(y_test, y_pred, labels=list(range(1, n_classes + 1)))
    pd.DataFrame(cm).to_csv(OUT_DIR / f"confusion_matrix_{tag}.csv", index=False, encoding="utf-8-sig")

    # PNGs
    save_cm_png(cm, n_classes=n_classes, tag=tag)
    save_or_png(coef_df, tag=tag, top_n=10)

    results.append({"target": tag, "n_classes": n_classes, "distribution": best_distr, **mets})


# 3 clases (comparativo)
fit_and_eval("confianza_3", n_classes=3, tag="ordinal_logit_3clases")

# 5 niveles (modelo ordinal recomendado)
fit_and_eval(TARGET_5, n_classes=5, tag="ordinal_logit_5niveles")


# =========================
# Save metrics
# =========================
res_df = pd.DataFrame(results).sort_values("f1_weighted", ascending=False)
res_df.to_csv(OUT_DIR / "metrics.csv", index=False, encoding="utf-8-sig")

best = res_df.iloc[0].to_dict()

print("\nResultados (mayor a menor por f1_weighted):")
print(res_df)

print("\nMejor configuración (según f1_weighted):")
print(best)

(OUT_DIR / "best_model_choice.txt").write_text(
    "Mejor según f1_weighted:\n" + str(best),
    encoding="utf-8"
)

print("\nGuardado en:", OUT_DIR)
print("Figuras ordinal en:", FIG_DIR)
