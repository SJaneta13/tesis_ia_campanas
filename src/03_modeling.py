# src/03_modeling.py
import os
import json
import shutil
import joblib
import warnings
import time
import numpy as np
import pandas as pd
import textwrap
import sys
from pathlib import Path

from scipy.stats import loguniform
from src.plotting_style import set_paper_style, save_figure, prettify_and_shorten

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Estabilidad: evitar problemas de joblib en Windows/OneDrive
os.environ["LOKY_MAX_CPU_COUNT"] = "1"

from datetime import datetime


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, RandomizedSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, label_binarize
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix, roc_auc_score

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.base import clone
import argparse


# =========================
# CONFIG
# =========================
parser = argparse.ArgumentParser()

parser.add_argument(
    "--target",
    choices=["5", "3"],
    default="5",
    help="Configuración de la variable objetivo: 5 niveles o 3 clases.",
)

parser.add_argument(
    "--input",
    default="data/processed/encuestas/model_ready_no_text.csv",
    help="Ruta del conjunto de datos preparado para modelado.",
)

parser.add_argument(
    "--sensitivity",
    action="store_true",
    help=(
        "Ejecuta el análisis de sensibilidad excluyendo predictores "
        "conceptualmente relacionados con confianza o transparencia electoral."
    ),
)

args = parser.parse_args()

INPUT_PATH = args.input
USE_TARGET_3 = (args.target == "3")
SENSITIVITY_ANALYSIS = bool(args.sensitivity)

#pruebas 
FAST_DEBUG = False  # True = prueba rápida; False = corrida final tesis

TARGET_5 = "confianza_idx_round"   # 1..5

TEST_SIZE = 0.30                   # 70/30
N_SPLITS = 5 if not FAST_DEBUG else 3                   # CV interno
N_JOBS = 1                         # estabilidad Windows/OneDrive

SEEDS = [0, 7, 13, 21, 42] if not FAST_DEBUG else [0]

# Feature selection
USE_FEATURE_SELECTION = False
FS_THRESHOLD = "mean"



# Search
RANDOM_SEARCH_N_ITER = 120 if not FAST_DEBUG else 15       # ↑ recomendado para SVM y RF
REFIT_METRIC = "f1_weighted"
SCORING_DICT = {
    "f1_weighted": "f1_weighted",
    "f1_macro": "f1_macro",
    "accuracy": "accuracy",
}

# Feature selection por modelo (evitar dañar SVM)
USE_FS_MODELS = {"random_forest"}  # puedes añadir "voting_ensemble" si quieres

# Guardado por run
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

RUN_SUFFIX = "_sensitivity" if SENSITIVITY_ANALYSIS else "_complete"

RUN_DIR = Path("outputs") / "runs" / f"run_{RUN_ID}{RUN_SUFFIX}"

DIR_FIGURES = RUN_DIR / "figures"
DIR_TABLES  = RUN_DIR / "tables"
DIR_MODELS  = RUN_DIR / "models"
DIR_LOGS    = RUN_DIR / "logs"
for d in [DIR_FIGURES, DIR_TABLES, DIR_MODELS, DIR_LOGS]:
    d.mkdir(parents=True, exist_ok=True)

print(f"Run guardado en: {RUN_DIR}")


# =========================
# MÉTRICAS ORDINALES
# =========================
def mae_ordinal(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))

def quadratic_weighted_kappa(y_true, y_pred, min_rating=1, max_rating=5):
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    K = max_rating - min_rating + 1
    O = np.zeros((K, K), dtype=float)
    for a, p in zip(y_true, y_pred):
        O[a - min_rating, p - min_rating] += 1

    act_hist = np.bincount(y_true - min_rating, minlength=K).astype(float)
    pred_hist = np.bincount(y_pred - min_rating, minlength=K).astype(float)

    E = np.outer(act_hist, pred_hist)
    if E.sum() > 0:
        E = E / E.sum() * O.sum()

    W = np.zeros((K, K), dtype=float)
    for i in range(K):
        for j in range(K):
            W[i, j] = ((i - j) ** 2) / ((K - 1) ** 2)

    num = float((W * O).sum())
    den = float((W * E).sum())
    return float(1 - (num / den if den != 0 else 0))



set_paper_style()

# =========================
# PAPER STYLE (Nature/IEEE-like)
# =========================
PAPER_DPI = 450  # 300 mínimo; 450 recomendado para Word
SAVE_VECTOR = True  # también guarda PDF

# =========================
# PLOTS
# =========================

def class_labels(use_target_3: bool):
    if use_target_3:
        return ["Baja", "Media", "Alta"]
    return ["1", "2", "3", "4", "5"]



# =========================
def plot_confusion_matrix_paper(cm, labels, title, out_path_base, normalize="true"):
    """
    cm: confusion_matrix counts
    labels: list[str]
    normalize: "true" (por fila), None (conteos)
    out_path_base: sin extensión. Se guardará .png y opcionalmente .pdf
    """
    cm = np.array(cm, dtype=float)

    if normalize == "true":
        row_sums = cm.sum(axis=1, keepdims=True)
        show = np.divide(cm, row_sums, out=np.zeros_like(cm), where=row_sums != 0)
    else:
        show = cm


    fig, ax = plt.subplots(figsize=(3.45, 3.2), constrained_layout=True)
    im = ax.imshow(show, interpolation="nearest", cmap="Blues")

    # ticks
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Real")

    # título corto (máx 1–2 líneas)
    ax.set_title("\n".join(textwrap.wrap(title, width=42)))

    # anotaciones
    for i in range(show.shape[0]):
        for j in range(show.shape[1]):
            if normalize == "true":
                txt = f"{show[i, j]*100:.0f}%\n(n={int(cm[i, j])})"
            else:
                txt = f"{int(show[i, j])}"    
            ax.text(j, i, txt, ha="center", va="center", fontsize=7)

    # barra de color solo si normalizas (más interpretable)
    if normalize == "true":
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("Proporción (por clase real)")

    # Guardado alta calidad
    save_figure(fig, Path(out_path_base), dpi=PAPER_DPI, save_png=True, save_pdf=SAVE_VECTOR, save_svg=False)

    plt.close(fig)



def plot_rf_importance(fi_df, top_n, title, out_path_base):
    top = fi_df.head(top_n).copy()

    top["feature_short"] = top["feature"].apply(
        lambda x: prettify_and_shorten(x, max_len=38 if top_n <= 10 else 44)
    )

   
    fig_height = 4.6 if top_n <= 10 else 7.0
    fig_width = 6.8 if top_n <= 10 else 7.4

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    ax.barh(top["feature_short"][::-1], top["importance"][::-1])
    ax.set_xlabel("Importancia de Variable")
    ax.set_ylabel("")
    ax.set_title(title, pad=10)
    ax.tick_params(axis="y", labelsize=8)
    ax.tick_params(axis="x", labelsize=8)

    plt.subplots_adjust(left=0.42, right=0.98, top=0.90, bottom=0.10)

    save_figure(
        fig,
        Path(out_path_base),
        dpi=600,
        save_png=True,
        save_pdf=True,
        save_svg=False
    )
    plt.close(fig)



# =========================
# LOAD DATA
# =========================
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
print("Dataset para modelado:", df.shape)

df = df.dropna(subset=[TARGET_5]).copy()
df[TARGET_5] = df[TARGET_5].astype(int)

print("\nDistribución del target (confianza_idx_round):")
print(df[TARGET_5].value_counts().sort_index())

if USE_TARGET_3:
    def to_3_classes(x):
        if x <= 2:
            return 1
        elif x == 3:
            return 2
        else:
            return 3

    df["confianza_3"] = df[TARGET_5].apply(to_3_classes).astype(int)
    target_col = "confianza_3"
    labels = [1, 2, 3]
    print("\nDistribución target 3 (1=baja,2=media,3=alta):")
    print(df[target_col].value_counts().sort_index())
else:
    target_col = TARGET_5
    labels = [1, 2, 3, 4, 5]


# =========================
# FEATURE SELECTION (DROP)
# =========================

# Predictores conceptualmente solapados con la variable objetivo.
#
# No contienen directamente confianza_idx, pero sus enunciados ya incorporan
# juicios sobre confianza o transparencia electoral. Se excluyen únicamente
# en el análisis de sensibilidad.
CONCEPTUAL_OVERLAP_COLS = [
    (
        "Percepción sobre el uso de IA en campañas políticas "
        "[La presencia de bots o cuentas falsas en redes sociales "
        "reduce mi confianza en la información política digital.]"
    ),
    (
        "Percepción sobre el uso de IA en campañas políticas "
        "[La presencia de bots o cuentas falsas en redes sociales "
        "reduce mi confianza en la información política digital.]_num"
    ),
    (
        "Percepción sobre el uso de IA en campañas políticas "
        "[La inteligencia artificial puede mejorar la transparencia "
        "del proceso electoral.]"
    ),
    (
        "Percepción sobre el uso de IA en campañas políticas "
        "[La inteligencia artificial puede mejorar la transparencia "
        "del proceso electoral.]_num"
    ),
    (
        "¿Ha cambiado su confianza en el proceso electoral al saber que "
        "existen bots, deepfakes o manipulación mediante IA?"
    ),
]

DROP_COLS = [
    "confianza_idx", "confianza_idx_round",
    "limpieza_num", "fraude_num", "fraude_rev",
    "confianza_limpieza", "confianza_fraude",
]

if SENSITIVITY_ANALYSIS:
    overlap_present = [
        col for col in CONCEPTUAL_OVERLAP_COLS if col in df.columns
    ]

    overlap_missing = [
        col for col in CONCEPTUAL_OVERLAP_COLS if col not in df.columns
    ]

    DROP_COLS.extend(overlap_present)

    print("\nANÁLISIS DE SENSIBILIDAD ACTIVADO")
    print("Predictores conceptualmente solapados que serán excluidos:")

    for col in overlap_present:
        print(f" - {col}")

    if overlap_missing:
        print("\nPredictores definidos pero no encontrados en el dataset:")

        for col in overlap_missing:
            print(f" - {col}")
else:
    print("\nMODELO COMPLETO: se conservan los predictores perceptuales.")

if "confianza_3" in df.columns:
    DROP_COLS.append("confianza_3")
if "Marca temporal" in df.columns:
    DROP_COLS.append("Marca temporal")

TEXT_COL = (
    "¿Qué recomendaciones haría para garantizar un uso responsable y transparente de la "
    "inteligencia artificial en campañas políticas digitales en Ecuador, considerando la "
    "experiencia de la campaña entre Luisa González y Daniel Noboa?"
)
if TEXT_COL in df.columns:
    DROP_COLS.append(TEXT_COL)

for c in df.columns:
    if isinstance(c, str) and c.startswith("Unnamed"):
        DROP_COLS.append(c)

X = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors="ignore")
y = df[target_col].copy()

excluded_overlap_df = pd.DataFrame(
    {
        "variable": [
            col for col in CONCEPTUAL_OVERLAP_COLS if col in df.columns
        ],
        "excluded_in_this_run": [
            bool(SENSITIVITY_ANALYSIS)
            for col in CONCEPTUAL_OVERLAP_COLS
            if col in df.columns
        ],
        "reason": (
            "Solapamiento conceptual con confianza o transparencia electoral"
        ),
    }
)

excluded_overlap_df.to_csv(
    DIR_TABLES / "conceptual_overlap_variables.csv",
    index=False,
    encoding="utf-8-sig",
)

num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = [c for c in X.columns.tolist() if c not in num_cols]

print("\nColumnas numéricas detectadas:", len(num_cols))
print("Columnas categóricas detectadas:", len(cat_cols))
print("Features usadas:", X.shape[1])
print("Ejemplo columnas:", X.columns.tolist()[:8])


# =========================
# PREPROCESS
# =========================
try:
    ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
except TypeError:
    ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)

preprocess = ColumnTransformer(
    transformers=[
        ("num", Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), num_cols),
        ("cat", Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", ohe),
        ]), cat_cols),
    ],
    remainder="drop"
)


# =========================
# MODELS + GRIDS
# =========================
models = {
    "baseline_majority": {
        "estimator": DummyClassifier(strategy="most_frequent", random_state=0),
        "param_grid": {},
        "search": "none",
    },
    "baseline_stratified": {
        "estimator": DummyClassifier(strategy="stratified", random_state=0),
        "param_grid": {},
        "search": "none",
    },

    # Nuevo: baseline fuerte lineal
    "log_reg": {
        "estimator": LogisticRegression(
            max_iter=5000,
            class_weight="balanced",
            solver="lbfgs",
            
        ),
        "param_grid": {
            "clf__C": [0.01, 0.1, 1, 10, 100],
        },
        "search": "grid",
    },

    "random_forest": {
        "estimator": RandomForestClassifier(
            random_state=0,
            n_jobs=1
        ),
        "param_grid": {
            "clf__n_estimators": [200, 400, 600],
            "clf__max_depth": [None, 10, 20, 30],
            "clf__min_samples_split": [2, 5, 10],
            "clf__min_samples_leaf": [1, 2, 4],
            "clf__max_features": ["sqrt", "log2", None],
            "clf__bootstrap": [True, False],
            "clf__max_samples": [None, 0.8, 0.9],
            "clf__class_weight": ["balanced", "balanced_subsample"],
        },
        "search": "random",
        "n_iter": 60,  
    },

    # SVM: mejor coverage con loguniform
    "svm_rbf": {
        "estimator": SVC(
            kernel="rbf",
            class_weight="balanced",
            probability=True
        ),
        "param_grid": {
            "clf__C": loguniform(1e-2, 1e3),
            "clf__gamma": loguniform(1e-5, 1e0),
        },
        "search": "random",
        "n_iter": 60,   # 60 suele mantener calidad con loguniform
    },

    "hist_gradient_boosting": {
        "estimator": HistGradientBoostingClassifier(
            random_state=0,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=20
        ),
        "param_grid": {
            "clf__learning_rate": [0.01, 0.05, 0.1, 0.2],
            "clf__max_iter": [150, 250, 400],
            "clf__max_depth": [None, 5, 10, 20],
            "clf__min_samples_leaf": [10, 20, 30],
            "clf__l2_regularization": [0.0, 0.1, 1.0],
        },
        "search": "random",
        "n_iter": 25, 
    },

    "voting_ensemble": {
        "estimator": VotingClassifier(
            estimators=[
                ("rf", RandomForestClassifier(n_estimators=400, max_depth=20, class_weight="balanced", random_state=0, n_jobs=1)),
                ("hgb", HistGradientBoostingClassifier(learning_rate=0.1, max_iter=250, random_state=0)),
            ],
            voting="soft"
        ),
        "param_grid": {
            "clf__voting": ["soft"]
        },
        "search": "none",
    },
}


# =========================
# EVALUATION HELPERS
# =========================
def compute_auc_ovr(y_true, y_proba, n_classes):
    try:
        y_true = np.asarray(y_true)
        if y_proba is None:
            return float("nan")

        y_proba = np.asarray(y_proba)

        if y_proba.ndim == 1:
            y_proba = y_proba.reshape(-1, 1)

        if y_proba.ndim == 2 and y_proba.shape[1] != n_classes:
            return float("nan")

        y_bin = label_binarize(y_true, classes=list(range(1, n_classes + 1)))
        if y_bin.shape[1] == 1:
            return float(roc_auc_score(y_bin, y_proba[:, :1]))
        return float(roc_auc_score(y_bin, y_proba, multi_class="ovr", average="weighted"))
    except Exception:
        return float("nan")


def evaluate_predictions(y_true, y_pred, use_target_3, y_proba=None):
    acc = accuracy_score(y_true, y_pred)
    f1m = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1w = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    mae = mae_ordinal(y_true, y_pred)
    n_classes = 3 if use_target_3 else 5
    qwk = quadratic_weighted_kappa(y_true, y_pred, min_rating=1, max_rating=n_classes)
    auc = compute_auc_ovr(y_true, y_proba, n_classes)
    return {
        "accuracy": float(acc),
        "f1_macro": float(f1m),
        "f1_weighted": float(f1w),
        "mae_ordinal": float(mae),
        "kappa_qw": float(qwk),
        "auc_ovr": float(auc),
    }


def aggregate_seed_metrics(seed_metrics_list):
    keys = seed_metrics_list[0].keys()
    out = {}
    for k in keys:
        vals = [d[k] for d in seed_metrics_list]
        out[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals, ddof=0))}
    return out


def grid_size(param_grid: dict) -> int:
    if not param_grid:
        return 0
    size = 1
    for v in param_grid.values():
        if hasattr(v, "rvs"):
            return 10**9
        size *= max(1, len(v))
    return size


def with_seed(estimator, seed: int):
    """Clona y setea random_state si aplica (para RF/HGB/etc.)."""
    est = clone(estimator)
    if hasattr(est, "random_state"):
        try:
            est.set_params(random_state=seed)
        except Exception:
            pass
    return est


# =========================
# MAIN LOOP
# =========================
rows_run_level = []
rows_seed_level = []
rf_importance_saved = False

for model_name, cfg in models.items():
    print("\n==============================")
    print("Modelo:", model_name)
    print("==============================")

    per_seed_metrics = []

    for seed in SEEDS:
        t_start = time.perf_counter()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=TEST_SIZE,
            random_state=seed,
            stratify=y
        )

        cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=seed)

        # Estimador con random_state = seed si corresponde
        base_estimator = with_seed(cfg["estimator"], seed)

        # Pipeline: FS solo para RF (y solo si está activado)
        if model_name.startswith("baseline") or (not USE_FEATURE_SELECTION) or (model_name not in USE_FS_MODELS):
            pipe = Pipeline(steps=[
                ("prep", preprocess),
                ("clf", base_estimator),
            ])
        else:
            selector_rf = RandomForestClassifier(n_estimators=400, random_state=seed, n_jobs=1)
            pipe = Pipeline(steps=[
                ("prep", preprocess),
                ("feature_selection", SelectFromModel(selector_rf, threshold=FS_THRESHOLD)),
                ("clf", base_estimator),
            ])

        best_model = None
        best_params = {}
        cv_f1w_mean = 0.0
        cv_f1w_std = 0.0

        search_mode = cfg.get("search", "random")

        if search_mode == "none" or not cfg["param_grid"]:
            best_model = pipe.fit(X_train, y_train)
        else:

            has_distributions = any(hasattr(v, "rvs") for v in cfg["param_grid"].values())
            if has_distributions:
                use_random = True
            else:
                gsize = grid_size(cfg["param_grid"])
                use_random = not (search_mode == "grid" and gsize <= RANDOM_SEARCH_N_ITER)

            if (search_mode == "grid") and (not has_distributions) and (gsize <= RANDOM_SEARCH_N_ITER):
                search = GridSearchCV(
                    estimator=pipe,
                    param_grid=cfg["param_grid"],
                    scoring=SCORING_DICT,
                    refit=REFIT_METRIC,
                    cv=cv,
                    n_jobs=N_JOBS,
                    return_train_score=True,
                    verbose=2
                )
            else:
                search = RandomizedSearchCV(
                    estimator=pipe,
                    param_distributions=cfg["param_grid"],
                    n_iter=cfg.get("n_iter", RANDOM_SEARCH_N_ITER),
                    scoring=SCORING_DICT,
                    refit=REFIT_METRIC,
                    cv=cv,
                    n_jobs=N_JOBS,
                    random_state=seed,
                    return_train_score=True,
                    verbose=2
                )
            print(f"  -> {model_name} | seed={seed} | start search | {time.strftime('%H:%M:%S')}")
            search.fit(X_train, y_train)
            print(f"  <- {model_name} | seed={seed} | end search   | {time.strftime('%H:%M:%S')} | elapsed={time.perf_counter()-t_start:.1f}s")
            best_model = search.best_estimator_
            best_params = search.best_params_

            best_idx = search.best_index_
            cv_f1w_mean = float(search.cv_results_[f"mean_test_{REFIT_METRIC}"][best_idx])
            cv_f1w_std  = float(search.cv_results_[f"std_test_{REFIT_METRIC}"][best_idx])

        # Test
        y_pred = best_model.predict(X_test)

        # Probabilidades para AUC (multiclase)
        y_proba = None
        try:
            if hasattr(best_model, "predict_proba"):
                y_proba = best_model.predict_proba(X_test)
        except Exception:
            y_proba = None

        t_elapsed = time.perf_counter() - t_start

        metrics = evaluate_predictions(y_test, y_pred, use_target_3=USE_TARGET_3, y_proba=y_proba)
        metrics["time_seconds"] = round(float(t_elapsed), 2)

        rows_seed_level.append({
            "run_id": RUN_ID,
            "model": model_name,
            "seed": seed,
            "target": target_col,
            "n_train": int(len(y_train)),
            "n_test": int(len(y_test)),
            **metrics,
            "cv_f1_weighted_mean": float(cv_f1w_mean),
            "cv_f1_weighted_std": float(cv_f1w_std),
            "best_params": json.dumps(best_params, ensure_ascii=False),
        })

        per_seed_metrics.append(metrics)

        # Artefactos solo para seed=SEEDS[0]
        if seed == SEEDS[0]:
            report = classification_report(y_test, y_pred, zero_division=0)
            cm = confusion_matrix(y_test, y_pred, labels=labels)

            row_sums = cm.sum(axis=1, keepdims=True)
            recall_by_class = np.divide(
                cm.diagonal(),
                row_sums.flatten(),
                out=np.zeros(len(labels), dtype=float),
                where=row_sums.flatten() != 0
            )

            pd.DataFrame({
                "class": labels,
                "recall": recall_by_class
            }).to_csv(DIR_TABLES / f"class_recall_{model_name}_{RUN_ID}.csv", index=False, encoding="utf-8-sig")
            
            
            lab = class_labels(USE_TARGET_3)
            cm_path_base = str(DIR_FIGURES / f"cm_{model_name}_{RUN_ID}_norm")
            short_title = f"Matriz de confusión normalizada"
            plot_confusion_matrix_paper(cm, labels=lab, title=short_title, out_path_base=cm_path_base, normalize="true")


            (DIR_TABLES / f"report_{model_name}_{RUN_ID}.txt").write_text(report, encoding="utf-8")

            model_path = DIR_MODELS / f"{model_name}_{RUN_ID}.joblib"
            joblib.dump(best_model, model_path)

            params_path = DIR_MODELS / f"{model_name}_{RUN_ID}_params.json"
            params_path.write_text(
                json.dumps(best_params, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            # Importancia RF: solo si el clasificador final es RF
            if model_name == "random_forest":
                try:
                    feat_names = []
                    if len(num_cols) > 0:
                        feat_names.extend(num_cols)

                    ohe_step = best_model.named_steps["prep"].named_transformers_["cat"].named_steps["onehot"]
                    cat_feat = ohe_step.get_feature_names_out(cat_cols).tolist()
                    feat_names.extend(cat_feat)

                    if "feature_selection" in best_model.named_steps:
                        selector = best_model.named_steps["feature_selection"]
                        support = selector.get_support()
                        feat_names = [f for f, s in zip(feat_names, support) if s]

                    importances = best_model.named_steps["clf"].feature_importances_
                    fi_df = pd.DataFrame({"feature": feat_names, "importance": importances}).sort_values("importance", ascending=False)

                    fi_csv = DIR_TABLES / f"rf_feature_importance_{RUN_ID}.csv"
                    fi_df.to_csv(fi_csv, index=False, encoding="utf-8-sig")

                    fi_png_10 = DIR_FIGURES / f"rf_feature_importance_top10_{RUN_ID}.png"
                    plot_rf_importance(fi_df, top_n=10, title="Variables más influyentes (Random Forest)", out_path_base=fi_png_10)
                    
                    fi_png_20 = DIR_FIGURES / f"rf_feature_importance_top20_{RUN_ID}.png"
                    plot_rf_importance(fi_df, top_n=20, title="Variables más influyentes (anexo)", out_path_base=fi_png_20)

                    rf_importance_saved = True
                    print("Importancia RF guardada:", fi_csv)
                except Exception as e:
                    print("No se pudo extraer importancia de variables (RF). Error:", e)

    # Resumen por modelo (mean/std sobre seeds)
    agg = aggregate_seed_metrics(per_seed_metrics)
    rows_run_level.append({
        "run_id": RUN_ID,
        "model": model_name,
        "target": target_col,
        "n_total": int(len(df)),
        "n_features": int(X.shape[1]),
        "seeds": json.dumps(SEEDS),
        "test_size": float(TEST_SIZE),

        "accuracy_mean": agg["accuracy"]["mean"],
        "accuracy_std": agg["accuracy"]["std"],
        "f1_macro_mean": agg["f1_macro"]["mean"],
        "f1_macro_std": agg["f1_macro"]["std"],
        "f1_weighted_mean": agg["f1_weighted"]["mean"],
        "f1_weighted_std": agg["f1_weighted"]["std"],
        "mae_ordinal_mean": agg["mae_ordinal"]["mean"],
        "mae_ordinal_std": agg["mae_ordinal"]["std"],
        "kappa_qw_mean": agg["kappa_qw"]["mean"],
        "kappa_qw_std": agg["kappa_qw"]["std"],
        "auc_ovr_mean": agg["auc_ovr"]["mean"],
        "auc_ovr_std": agg["auc_ovr"]["std"],
        "time_seconds_mean": agg["time_seconds"]["mean"],
        "time_seconds_std": agg["time_seconds"]["std"],
        "analysis_mode": (
            "sensitivity_without_overlap"
            if SENSITIVITY_ANALYSIS
            else "complete_model"
        ),
        "conceptual_overlap_excluded": bool(SENSITIVITY_ANALYSIS),
        "n_overlap_variables_excluded": int(
            sum(col in df.columns for col in CONCEPTUAL_OVERLAP_COLS)
            if SENSITIVITY_ANALYSIS
            else 0
        ),
    })


# =========================
# SAVE OUTPUTS
# =========================
df_run = pd.DataFrame(rows_run_level)
df_seed = pd.DataFrame(rows_seed_level)

run_csv = DIR_TABLES / f"metrics_run_{RUN_ID}.csv"
run_json = DIR_TABLES / f"metrics_run_{RUN_ID}.json"
seed_csv = DIR_TABLES / f"metrics_by_seed_{RUN_ID}.csv"

df_run.to_csv(run_csv, index=False, encoding="utf-8-sig")
df_seed.to_csv(seed_csv, index=False, encoding="utf-8-sig")
run_json.write_text(df_run.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")

latest_dir = Path("outputs") / "latest"
if latest_dir.exists():
    shutil.rmtree(latest_dir)
shutil.copytree(RUN_DIR, latest_dir)

# =========================
# RESUMEN METODOLÓGICO
# =========================

methodology_summary = {
    "configuracion": "principal_5_niveles" if not USE_TARGET_3 else "complementaria_3_clases",
    "split": "70% entrenamiento / 30% validación",
    "validacion": "Stratified K-Fold interno",
    "n_splits": N_SPLITS,
    "seeds": SEEDS,
    "target": target_col,
    "metricas": [
        "accuracy",
        "f1_macro",
        "f1_weighted",
        "mae_ordinal",
        "kappa_qw",
        "auc_ovr"
    ],
    "nota": "El modelado tiene carácter exploratorio y no causal. En la tesis se reportan principalmente Random Forest, SVM-RBF y regresión logística ordinal."
}

(DIR_LOGS / "methodology_summary.json").write_text(
    json.dumps(methodology_summary, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("\n====================================")
print("Listo. Archivos generados:")
print(" - Run dir:", RUN_DIR)
print(" - Latest:", latest_dir)
print(" - Métricas (resumen):", run_csv)
print(" - Métricas por seed:", seed_csv)
print(" - JSON resumen:", run_json)
print(" - Figuras:", DIR_FIGURES)
print(" - Modelos:", DIR_MODELS)
if rf_importance_saved:
    print(" - Importancia RF: rf_feature_importance_*.csv y .png")
print("====================================")