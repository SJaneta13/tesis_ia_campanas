# src/03_modeling.py
import os
import json
import shutil
import joblib
import numpy as np
import pandas as pd

from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Backend no interactivo para evitar errores de tkinter en multithreading
import matplotlib.pyplot as plt

from sklearn.model_selection import (
    train_test_split, StratifiedKFold, GridSearchCV
)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

from sklearn.metrics import (
    accuracy_score, f1_score, classification_report, confusion_matrix, make_scorer
)
from sklearn.preprocessing import StandardScaler

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC



# =========================
# CONFIG
# =========================
INPUT_PATH = "data/processed/model_ready.csv"

TARGET_5 = "confianza_idx_round"   # 1..5
USE_TARGET_3 = True                # True => 3 clases (1=baja,2=media,3=alta); False => 5 clases

TEST_SIZE = 0.20
N_SPLITS = 5
N_JOBS = -1

# Semillas para análisis más estable (puedes ajustar)
SEEDS = [0, 7, 13, 21, 42]

# Guardado por run
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = Path("outputs") / "runs" / f"run_{RUN_ID}"
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
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def quadratic_weighted_kappa(y_true, y_pred, min_rating=1, max_rating=5):
    """QWK para ordinal 1..K (implementación simple)."""
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


# =========================
# PLOTS
# =========================
def plot_confusion_matrix(cm, labels, title, out_path):
    plt.figure()
    plt.imshow(cm)
    plt.title(title)
    plt.xlabel("Predicción")
    plt.ylabel("Real")
    plt.xticks(range(len(labels)), labels)
    plt.yticks(range(len(labels)), labels)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center")

    plt.colorbar()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_rf_importance(fi_df, top_n, title, out_path):
    plt.figure(figsize=(14, 10))
    top = fi_df.head(top_n).copy()

    # Acortar etiquetas largas para que el layout no falle
    def shorten(s, n=90):
        s = str(s)
        return s if len(s) <= n else s[:n] + "…"

    labels = [shorten(x) for x in top["feature"][::-1]]

    plt.barh(labels, top["importance"][::-1])
    plt.title(title)
    plt.xlabel("Importancia")

    # Más margen izquierdo para labels
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()



# =========================
# LOAD DATA
# =========================
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
print("Dataset para modelado:", df.shape)

df = df.dropna(subset=[TARGET_5]).copy()
df[TARGET_5] = df[TARGET_5].astype(int)

print("\nDistribución del target (confianza_idx_round):")
print(df[TARGET_5].value_counts().sort_index())

# Target 3 clases (opcional)
if USE_TARGET_3:
    def to_3_classes(x):
        if x <= 2:
            return 1  # baja
        elif x == 3:
            return 2  # media
        else:
            return 3  # alta

    df["confianza_3"] = df[TARGET_5].apply(to_3_classes).astype(int)
    target_col = "confianza_3"
    labels = [1, 2, 3]
    print("\nDistribución target 3 (1=baja,2=media,3=alta):")
    print(df[target_col].value_counts().sort_index())
else:
    target_col = TARGET_5
    labels = [1, 2, 3, 4, 5]

# =========================
# FEATURE SELECTION
# =========================
DROP_COLS = [
    "confianza_idx", "confianza_idx_round",
    "limpieza_num", "fraude_num", "fraude_rev",
    "confianza_limpieza", "confianza_fraude",
]
if "confianza_3" in df.columns:
    DROP_COLS.append("confianza_3")
if "Marca temporal" in df.columns:
    DROP_COLS.append("Marca temporal")

TEXT_COL = "¿Qué recomendaciones haría para garantizar un uso responsable y transparente de la inteligencia artificial en campañas políticas digitales en Ecuador, considerando la experiencia de la campaña entre Luisa González y Daniel Noboa?"
if TEXT_COL in df.columns:
    DROP_COLS.append(TEXT_COL)


X = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors="ignore")
y = df[target_col].copy()

# Detectar columnas
num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = [c for c in X.columns.tolist() if c not in num_cols]

print("\nColumnas numéricas detectadas:", len(num_cols))
print("Columnas categóricas detectadas:", len(cat_cols))
print("\nFeatures usadas:", X.shape[1])
print("Ejemplo columnas:", X.columns.tolist()[:8])


# =========================
# PREPROCESS
# =========================
# Nota: StandardScaler es crucial para SVM (sensible a escala).
# RF no se ve afectado por escalado, así que es seguro aplicarlo a ambos.
preprocess = ColumnTransformer(
    transformers=[
        ("num", Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())  # Mejora convergencia SVM
        ]), num_cols),
        ("cat", Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), cat_cols),
    ],
    remainder="drop"
)


# =========================
# MODELS + GRIDS
# =========================
# Para dataset pequeño (~1k encuestas): grids conservadores pero informativos
models = {
    # Baseline: estrategia "most_frequent" y "stratified" para comparación realista
    "baseline_majority": {
        "estimator": DummyClassifier(strategy="most_frequent", random_state=0),
        "param_grid": {}
    },
    "baseline_stratified": {
        "estimator": DummyClassifier(strategy="stratified", random_state=0),
        "param_grid": {}
    },
    # Random Forest: class_weight y criterion en grid para análisis completo
    # Según scikit-learn docs: criterion="gini" o "entropy" afecta splits
    "random_forest": {
        "estimator": RandomForestClassifier(
            random_state=0,
            max_features="sqrt",
            n_jobs=-1
        ),
        "param_grid": {
            "clf__n_estimators": [100, 200, 400],
            "clf__max_depth": [None, 8, 15],
            "clf__min_samples_split": [2, 5, 10],
            "clf__min_samples_leaf": [1, 2, 4],
            "clf__class_weight": ["balanced", "balanced_subsample"],
            "clf__criterion": ["gini", "entropy"],  # Añadido según doc oficial
        }
    },
    # SVM-RBF: grid en escala log para C, gamma más fino
    # Según scikit-learn docs: C controla regularización, gamma controla radio de influencia
    "svm_rbf": {
        "estimator": SVC(
            kernel="rbf",
            class_weight="balanced",
            random_state=0,
            probability=True  # Añadido para obtener probabilidades si se necesita
        ),
        "param_grid": {
            "clf__C": [0.1, 1, 10, 100],
            "clf__gamma": ["scale", "auto", 0.1, 0.01, 0.001]
        }
    }
}


# =========================
# EVALUATION HELPERS
# =========================
def evaluate_predictions(y_true, y_pred, use_target_3):
    acc = accuracy_score(y_true, y_pred)
    f1m = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1w = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    mae = mae_ordinal(y_true, y_pred)
    if use_target_3:
        qwk = quadratic_weighted_kappa(y_true, y_pred, min_rating=1, max_rating=3)
    else:
        qwk = quadratic_weighted_kappa(y_true, y_pred, min_rating=1, max_rating=5)
    return {
        "accuracy": float(acc),
        "f1_macro": float(f1m),
        "f1_weighted": float(f1w),
        "mae_ordinal": float(mae),
        "kappa_qw": float(qwk)
    }


def aggregate_seed_metrics(seed_metrics_list):
    """seed_metrics_list: list[dict(metric->value)] => dict(metric->(mean,std))."""
    keys = seed_metrics_list[0].keys()
    out = {}
    for k in keys:
        vals = [d[k] for d in seed_metrics_list]
        out[k] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals, ddof=0))
        }
    return out


# =========================
# MULTI-SCORING PARA GRIDSEARCHCV
# =========================
# Usar múltiples métricas evita optimizar solo una y da visión completa
SCORING_DICT = {
    "f1_weighted": "f1_weighted",
    "f1_macro": "f1_macro",
    "accuracy": "accuracy",
}
REFIT_METRIC = "f1_weighted"  # Métrica principal para seleccionar mejor modelo


# =========================
# MAIN LOOP
# =========================
rows_run_level = []          # 1 fila por modelo (promedio+std en seeds)
rows_seed_level = []         # 1 fila por (modelo, seed)
rf_importance_saved = False  # para guardar solo una vez (con el mejor seed promedio)

for model_name, cfg in models.items():
    print("\n==============================")
    print("Modelo:", model_name)
    print("==============================")

    # Guardar métricas por seed
    per_seed_metrics = []

    for seed in SEEDS:
        # Split estratificado por seed
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=TEST_SIZE,
            random_state=seed,
            stratify=y
        )

        cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=seed)

        pipe = Pipeline(steps=[
            ("prep", preprocess),
            ("clf", cfg["estimator"])
        ], memory=None)

        # Baseline no requiere grid
        if model_name.startswith("baseline"):
            best_model = pipe.fit(X_train, y_train)
            best_params = {}
            cv_f1w_mean = 0.0
            cv_f1w_std = 0.0
        else:
            # Multi-métrica: evalúa f1_weighted, f1_macro, accuracy simultáneamente
            grid = GridSearchCV(
                estimator=pipe,
                param_grid=cfg["param_grid"],
                scoring=SCORING_DICT,
                refit=REFIT_METRIC,  # Selecciona modelo por f1_weighted
                cv=cv,
                n_jobs=N_JOBS,
                return_train_score=True  # Para diagnóstico de overfitting
            )
            grid.fit(X_train, y_train)
            best_model = grid.best_estimator_
            best_params = grid.best_params_

            # Extraer CV scores del GridSearchCV (evita redundancia de cross_val_score)
            best_idx = grid.best_index_
            cv_f1w_mean = float(grid.cv_results_[f"mean_test_{REFIT_METRIC}"][best_idx])
            cv_f1w_std = float(grid.cv_results_[f"std_test_{REFIT_METRIC}"][best_idx])

        # Test
        y_pred = best_model.predict(X_test)
        metrics = evaluate_predictions(y_test, y_pred, use_target_3=USE_TARGET_3)

        # Guardar por seed
        rows_seed_level.append({
            "run_id": RUN_ID,
            "model": model_name,
            "seed": seed,
            "target": target_col,
            "n_train": int(len(y_train)),
            "n_test": int(len(y_test)),
            **metrics,
            "cv_f1_weighted_mean": cv_f1w_mean,
            "cv_f1_weighted_std": cv_f1w_std,
            "best_params": json.dumps(best_params, ensure_ascii=False),
        })

        per_seed_metrics.append(metrics)

        # Guardar artefactos SOLO para seed=SEEDS[0] (evita proliferación de archivos)
        # Nota: Para análisis de percepción ciudadana con ~1k encuestas, un modelo por tipo es suficiente
        if seed == SEEDS[0]:
            # Reporte y CM
            report = classification_report(y_test, y_pred, zero_division=0)
            cm = confusion_matrix(y_test, y_pred, labels=labels)

            report_path = DIR_TABLES / f"report_{model_name}_{RUN_ID}.txt"
            report_path.write_text(report, encoding="utf-8")

            cm_path = DIR_FIGURES / f"cm_{model_name}_{RUN_ID}.png"
            plot_confusion_matrix(
                cm,
                labels=labels,
                title=f"Matriz de confusión - {model_name} (target={target_col})",
                out_path=str(cm_path)
            )

            # Guardar modelo (baseline también se puede guardar)
            model_path = DIR_MODELS / f"{model_name}_{RUN_ID}.joblib"
            joblib.dump(best_model, model_path)

            # Importancia RF (solo si es RF)
            if model_name == "random_forest":
                try:
                    # Nombres post-transform (num + cat onehot)
                    feat_names = []

                    # num
                    if len(num_cols) > 0:
                        feat_names.extend(num_cols)

                    # cat
                    ohe = best_model.named_steps["prep"].named_transformers_["cat"].named_steps["onehot"]
                    cat_feat = ohe.get_feature_names_out(cat_cols).tolist()
                    feat_names.extend(cat_feat)

                    importances = best_model.named_steps["clf"].feature_importances_
                    fi_df = pd.DataFrame({
                        "feature": feat_names,
                        "importance": importances
                    }).sort_values("importance", ascending=False)

                    fi_csv = DIR_TABLES / f"rf_feature_importance_{RUN_ID}.csv"
                    fi_df.to_csv(fi_csv, index=False, encoding="utf-8-sig")

                    fi_png = DIR_FIGURES / f"rf_feature_importance_{RUN_ID}.png"
                    plot_rf_importance(
                        fi_df, top_n=20,
                        title="Importancia de variables – Random Forest",
                        out_path=str(fi_png)
                    )

                    rf_importance_saved = True
                    print("Importancia RF guardada:", fi_csv)
                except Exception as e:
                    print("No se pudo extraer importancia de variables (RF). Error:", e)

    # Agregar resumen por modelo (promedio+std en seeds)
    agg = aggregate_seed_metrics(per_seed_metrics)

    rows_run_level.append({
        "run_id": RUN_ID,
        "model": model_name,
        "target": target_col,
        "n_total": int(len(df)),
        "n_features": int(X.shape[1]),
        "seeds": json.dumps(SEEDS),
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

# Copia rápida a outputs/latest
latest_dir = Path("outputs") / "latest"
if latest_dir.exists():
    shutil.rmtree(latest_dir)
shutil.copytree(RUN_DIR, latest_dir)

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
