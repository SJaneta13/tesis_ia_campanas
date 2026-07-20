from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "outputs" / "runs"
TABLES_DIR = ROOT / "outputs" / "latest" / "tables"
MODEL_DIR = ROOT / "outputs" / "latest" / "models_dashboard"
DATA_CANDIDATES = [
    ROOT / "data" / "processed" / "encuestas" / "model_ready_no_text.csv",
    ROOT / "data" / "processed" / "encuestas" / "model_ready.csv",
]

TARGETS = {
    "5": "confianza_idx_round",
    "3": "confianza_3",
}

CONFIG_LABELS = {
    "5": "5 niveles",
    "3": "3 niveles",
}

CLASS_LABELS = {
    "5": {1: "Muy baja", 2: "Baja", 3: "Media", 4: "Alta", 5: "Muy alta"},
    "3": {1: "Baja", 2: "Media", 3: "Alta"},
}

MODEL_LABELS = {
    "random_forest": "Random Forest",
    "svm_rbf": "SVM",
    "log_reg": "Logistic Regression",
    "hist_gradient_boosting": "Gradient Boosting",
    "voting_ensemble": "Voting Ensemble",
}

DASHBOARD_MODELS = {
    "random_forest",
    "svm_rbf",
    "log_reg",
    "hist_gradient_boosting",
}

CONCEPTUAL_OVERLAP_COLS = {
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
}

PREFERRED_SIMULATOR_FEATURES = [
    "conoce_ia",
    "percibe_automatizacion",
    "identifica_ia",
    (
        "Durante la campaña presidencial entre Luisa González y Daniel Noboa, "
        "¿con qué frecuencia vio o recibió contenido político en redes sociales "
        "o plataformas digitales?"
    ),
    (
        "Percepción sobre el uso de IA en campañas políticas "
        "[Los partidos pueden manipular mi opinión mediante mensajes "
        "personalizados creados con IA.]"
    ),
    (
        "Percepción sobre el uso de IA en campañas políticas "
        "[Considero que el uso de inteligencia artificial en campañas políticas "
        "debería estar regulado por la ley.]"
    ),
    (
        "¿Considera que el uso de IA en campañas digitales influyó en su "
        "decisión de voto en las elecciones presidenciales de 2025?"
    ),
    (
        "¿Realiza alguna verificación (chequea fuentes, busca noticias, consulta "
        "otras personas) de la información política digital antes de compartirla?"
    ),
]

SIMULATOR_LABELS = {
    "conoce_ia": (
        "Conocimiento declarado de IA",
        "Conocimiento de IA",
        "Nivel declarado de familiaridad con la inteligencia artificial.",
    ),
    "percibe_automatizacion": (
        "Percepción de automatización",
        "Exposición digital",
        "Percepción de uso de automatización en contenidos de campaña.",
    ),
    "identifica_ia": (
        "Identificación de contenido con IA",
        "Alfabetización mediática",
        "Capacidad declarada para distinguir contenido generado o alterado con IA.",
    ),
    PREFERRED_SIMULATOR_FEATURES[3]: (
        "Frecuencia de exposición política digital",
        "Exposición digital",
        "Frecuencia con la que se recibió contenido político durante la campaña.",
    ),
    PREFERRED_SIMULATOR_FEATURES[4]: (
        "Riesgo de manipulación personalizada",
        "Riesgo percibido",
        "Percepción de posible manipulación mediante mensajes personalizados.",
    ),
    PREFERRED_SIMULATOR_FEATURES[5]: (
        "Necesidad de regulación",
        "Gobernanza de IA",
        "Valoración de la necesidad de regulación legal del uso de IA en campañas.",
    ),
    PREFERRED_SIMULATOR_FEATURES[6]: (
        "Influencia percibida de IA en el voto",
        "Influencia electoral",
        "Percepción de influencia de la IA en la decisión de voto.",
    ),
    PREFERRED_SIMULATOR_FEATURES[7]: (
        "Verificación de fuentes",
        "Alfabetización mediática",
        "Frecuencia de verificación antes de compartir información política.",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Consolida corridas de 5 y 3 niveles y genera los artefactos "
            "consumidos por dashboard/sections/modelos_predictivos.py."
        )
    )
    parser.add_argument(
        "--run-5",
        default=None,
        help="Nombre de la corrida de 5 niveles dentro de outputs/runs.",
    )
    parser.add_argument(
        "--run-3",
        default=None,
        help="Nombre de la corrida de 3 niveles dentro de outputs/runs.",
    )
    parser.add_argument(
        "--mode",
        choices=["sensitivity", "complete"],
        default="sensitivity",
        help="Modo de corridas que se buscará automáticamente.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin1")


def latest_file(folder: Path, pattern: str) -> Path:
    files = sorted(folder.glob(pattern))
    if not files:
        raise FileNotFoundError(
            f"No se encontró {pattern} dentro de {folder}"
        )
    return files[-1]


def load_run_metrics(run_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    tables = run_dir / "tables"
    summary = read_csv(latest_file(tables, "metrics_run_*.csv"))
    seeds = read_csv(latest_file(tables, "metrics_by_seed_*.csv"))
    return summary, seeds


def run_matches(run_dir: Path, target: str, mode: str) -> bool:
    try:
        summary, _ = load_run_metrics(run_dir)
    except Exception:
        return False

    if summary.empty or "target" not in summary.columns:
        return False

    expected_target = TARGETS[target]
    if not summary["target"].astype(str).eq(expected_target).any():
        return False

    expected_sensitivity = mode == "sensitivity"
    if "conceptual_overlap_excluded" in summary.columns:
        flag = (
            summary["conceptual_overlap_excluded"]
            .astype(str)
            .str.lower()
            .isin({"true", "1"})
            .any()
        )
        return flag == expected_sensitivity

    if "analysis_mode" in summary.columns:
        has_sensitivity = summary["analysis_mode"].astype(str).str.contains(
            "sensitivity", case=False, na=False
        ).any()
        return has_sensitivity == expected_sensitivity

    return not expected_sensitivity


def resolve_run(name: str | None, target: str, mode: str) -> Path:
    if name:
        run_dir = RUNS_DIR / name
        if not run_dir.exists():
            raise FileNotFoundError(f"No existe la corrida: {run_dir}")
        if not run_matches(run_dir, target, mode):
            raise ValueError(
                f"La corrida {name} no corresponde a target={target} "
                f"y mode={mode}."
            )
        return run_dir

    for run_dir in sorted(RUNS_DIR.glob("run_*"), reverse=True):
        if run_matches(run_dir, target, mode):
            return run_dir

    raise FileNotFoundError(
        f"No se encontró una corrida de {target} niveles en modo {mode}."
    )


def resolve_data() -> Path:
    for path in DATA_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError(
        "No se encontró model_ready_no_text.csv ni model_ready.csv."
    )


def to_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"true", "1", "yes", "si", "sí"})


def build_summary(
    summary_5: pd.DataFrame,
    summary_3: pd.DataFrame,
) -> pd.DataFrame:
    frames = []
    for target, source in [("5", summary_5), ("3", summary_3)]:
        df = source[source["model"].isin(DASHBOARD_MODELS)].copy()
        if df.empty:
            continue
        frames.append(
            pd.DataFrame(
                {
                    "Modelo": df["model"].map(MODEL_LABELS),
                    "Configuración": CONFIG_LABELS[target],
                    "AUC_OvR": pd.to_numeric(df["auc_ovr_mean"], errors="coerce"),
                    "Accuracy": pd.to_numeric(df["accuracy_mean"], errors="coerce"),
                    "F1_ponderado": pd.to_numeric(
                        df["f1_weighted_mean"], errors="coerce"
                    ),
                    "QWK": pd.to_numeric(df["kappa_qw_mean"], errors="coerce"),
                    "F1_macro": pd.to_numeric(df["f1_macro_mean"], errors="coerce"),
                    "MAE_ordinal": pd.to_numeric(
                        df["mae_ordinal_mean"], errors="coerce"
                    ),
                    "n": pd.to_numeric(df["n_total"], errors="coerce"),
                    "n_features": pd.to_numeric(
                        df["n_features"], errors="coerce"
                    ),
                    "analysis_mode": df.get("analysis_mode", ""),
                }
            )
        )

    if not frames:
        raise ValueError("No se encontraron modelos válidos para el resumen.")

    return pd.concat(frames, ignore_index=True)


def build_seed_table(seed_5: pd.DataFrame, seed_3: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for target, source in [("5", seed_5), ("3", seed_3)]:
        df = source[source["model"].isin(DASHBOARD_MODELS)].copy()
        if df.empty:
            continue
        frames.append(
            pd.DataFrame(
                {
                    "Modelo": df["model"].map(MODEL_LABELS),
                    "Configuración": CONFIG_LABELS[target],
                    "Seed": pd.to_numeric(df["seed"], errors="coerce"),
                    "AUC_OvR": pd.to_numeric(df["auc_ovr"], errors="coerce"),
                    "Accuracy": pd.to_numeric(df["accuracy"], errors="coerce"),
                    "F1_ponderado": pd.to_numeric(
                        df["f1_weighted"], errors="coerce"
                    ),
                    "QWK": pd.to_numeric(df["kappa_qw"], errors="coerce"),
                }
            )
        )

    if not frames:
        raise ValueError("No se encontraron métricas por semilla.")

    return pd.concat(frames, ignore_index=True)


def model_path(run_dir: Path, model_name: str) -> Path:
    return latest_file(run_dir / "models", f"{model_name}_*.joblib")


def model_feature_columns(model: Any) -> list[str]:
    columns = getattr(model, "feature_names_in_", None)
    if columns is None and hasattr(model, "named_steps"):
        prep = model.named_steps.get("prep") or model.named_steps.get("preprocessor")
        columns = getattr(prep, "feature_names_in_", None)
    if columns is None:
        raise ValueError(
            "El pipeline no conserva feature_names_in_. No se puede reconstruir X."
        )
    return [str(column) for column in columns]


def prepare_xy(
    df: pd.DataFrame,
    model: Any,
    target: str,
) -> tuple[pd.DataFrame, pd.Series]:
    target_col = TARGETS[target]
    if target_col not in df.columns:
        raise KeyError(f"Falta la variable objetivo {target_col} en el dataset.")

    columns = model_feature_columns(model)
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise KeyError(
            "Faltan predictores del pipeline en el dataset:\n- "
            + "\n- ".join(missing)
        )

    y = pd.to_numeric(df[target_col], errors="coerce")
    mask = y.notna()
    X = df.loc[mask, columns].copy()
    y = y.loc[mask].astype(int)
    return X, y


def build_confusion_artifact(
    df: pd.DataFrame,
    run_dir: Path,
    target: str,
    model_name: str,
) -> pd.DataFrame:
    model = joblib.load(model_path(run_dir, model_name))
    X, y = prepare_xy(df, model, target)

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=0,
        stratify=y,
    )
    y_pred = model.predict(X_test)

    numeric_labels = sorted(CLASS_LABELS[target])
    matrix = confusion_matrix(y_test, y_pred, labels=numeric_labels)

    rows = []
    for i, real in enumerate(numeric_labels):
        for j, predicted in enumerate(numeric_labels):
            rows.append(
                {
                    "Real": CLASS_LABELS[target][real],
                    "Predicho": CLASS_LABELS[target][predicted],
                    "Cantidad": int(matrix[i, j]),
                    "Modelo": MODEL_LABELS[model_name],
                    "Configuración": CONFIG_LABELS[target],
                }
            )
    return pd.DataFrame(rows)


def build_defaults(X: pd.DataFrame) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for column in X.columns:
        series = X[column]
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().mean() >= 0.80:
            defaults[column] = float(numeric.median())
        else:
            mode = series.dropna().astype(str).mode()
            defaults[column] = str(mode.iloc[0]) if not mode.empty else ""
    return defaults


def pretty_label(column: str) -> str:
    if column in SIMULATOR_LABELS:
        return SIMULATOR_LABELS[column][0]
    return str(column).replace("_", " ").strip().capitalize()


def permutation_feature_importance(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
) -> pd.DataFrame:
    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=0,
        stratify=y,
    )
    result = permutation_importance(
        model,
        X_test,
        y_test,
        scoring="f1_weighted",
        n_repeats=8,
        random_state=42,
        n_jobs=1,
    )
    importance = np.clip(result.importances_mean, a_min=0.0, a_max=None)
    if float(importance.sum()) == 0:
        importance = np.abs(result.importances_mean)
    total = float(importance.sum())
    normalized = importance / total if total else importance

    output = pd.DataFrame(
        {
            "Variable": X.columns,
            "Importancia": normalized,
            "Importancia_pct": normalized * 100,
        }
    )
    output["Etiqueta"] = output["Variable"].map(pretty_label)
    return output.sort_values("Importancia", ascending=False).reset_index(drop=True)


def ordered_options(series: pd.Series) -> list[str]:
    values = series.dropna().astype(str).str.strip()
    values = values[values.ne("")]
    if values.empty:
        return ["No disponible"]

    preferred_orders = [
        ["Nunca", "Rara vez", "A veces", "Frecuentemente", "Siempre"],
        [
            "Totalmente en desacuerdo",
            "En desacuerdo",
            "Ni de acuerdo ni en desacuerdo",
            "De acuerdo",
            "Totalmente de acuerdo",
        ],
        ["Nada", "Poco", "Sí, algo", "Sí, mucho", "No sé/no aplica"],
        ["No", "No estoy seguro/a", "Sí"],
    ]

    available = values.unique().tolist()
    for order in preferred_orders:
        if set(available).issubset(set(order)):
            return [item for item in order if item in available]
    return sorted(available)


def build_simulator_schema(
    X: pd.DataFrame,
    importance: pd.DataFrame,
    max_features: int = 6,
) -> pd.DataFrame:
    weight_map = dict(zip(importance["Variable"], importance["Importancia"]))
    available = [
        feature
        for feature in PREFERRED_SIMULATOR_FEATURES
        if feature in X.columns and feature not in CONCEPTUAL_OVERLAP_COLS
    ]

    if len(available) < max_features:
        extra = [
            feature
            for feature in importance["Variable"].tolist()
            if feature in X.columns
            and feature not in available
            and feature not in CONCEPTUAL_OVERLAP_COLS
            and X[feature].dropna().nunique() <= 12
        ]
        available.extend(extra)

    rows = []
    for feature in available[:max_features]:
        label, group, description = SIMULATOR_LABELS.get(
            feature,
            (pretty_label(feature), "Predictor", "Variable incluida en el modelo."),
        )
        options = ordered_options(X[feature])
        mode = X[feature].dropna().astype(str).mode()
        default = str(mode.iloc[0]) if not mode.empty else options[0]
        rows.append(
            {
                "Variable": feature,
                "Etiqueta": label,
                "Tipo": "categórica",
                "Opciones": "|".join(options),
                "Valor_por_defecto": default,
                "Grupo": group,
                "Descripcion": description,
                "Peso": float(weight_map.get(feature, 0.0)),
            }
        )
    return pd.DataFrame(rows).sort_values("Peso", ascending=False)


def build_interpretation_table(
    X: pd.DataFrame,
    importance: pd.DataFrame,
) -> pd.DataFrame:
    top = importance.head(4).copy()
    max_importance = float(top["Importancia"].max()) if not top.empty else 1.0
    rows = []
    for _, row in top.iterrows():
        variable = str(row["Variable"])
        support = float(X[variable].notna().mean()) if variable in X.columns else 0.0
        relative = (
            float(row["Importancia"]) / max_importance
            if max_importance > 0
            else 0.0
        )
        rows.append(
            {
                "Condición": f"Predictor: {row['Etiqueta']}",
                "Predicción": "Influencia relativa",
                "Soporte": support,
                "Confianza": relative,
                "Descripción": (
                    "Importancia por permutación en el conjunto de validación. "
                    "Indica contribución predictiva relativa y no causalidad."
                ),
            }
        )
    return pd.DataFrame(rows)


def build_simulator_artifacts(
    df: pd.DataFrame,
    run_5: Path,
    summary_5: pd.DataFrame,
) -> None:
    source_model = joblib.load(model_path(run_5, "random_forest"))
    X, y_numeric = prepare_xy(df, source_model, "5")

    importance = permutation_feature_importance(source_model, X, y_numeric)
    schema = build_simulator_schema(X, importance)
    defaults = build_defaults(X)
    interpretation = build_interpretation_table(X, importance)

    # Reajuste para despliegue: misma arquitectura e hiperparámetros, muestra completa,
    # clases con etiquetas legibles para el backend del simulador.
    deployment_model = clone(source_model)
    y_text = y_numeric.map(CLASS_LABELS["5"])
    deployment_model.fit(X, y_text)

    joblib.dump(
        deployment_model,
        MODEL_DIR / "simulator_best_model_5niveles.joblib",
    )
    (TABLES_DIR / "simulator_defaults_5niveles.json").write_text(
        json.dumps(defaults, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (MODEL_DIR / "model_classes_5niveles.json").write_text(
        json.dumps({"classes": list(CLASS_LABELS["5"].values())}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    rf_row = summary_5[summary_5["model"].eq("random_forest")]
    metrics = rf_row.iloc[0].to_dict() if not rf_row.empty else {}
    metadata = {
        "modelo_final": "Random Forest",
        "configuracion": "5 niveles",
        "variable_objetivo": TARGETS["5"],
        "n_registros": int(len(y_numeric)),
        "features": int(X.shape[1]),
        "run_origen": run_5.name,
        "analysis_mode": metrics.get("analysis_mode", ""),
        "conceptual_overlap_excluded": bool(
            str(metrics.get("conceptual_overlap_excluded", "")).lower()
            in {"true", "1"}
        ),
        "metricas_multisemilla": {
            "accuracy": metrics.get("accuracy_mean"),
            "f1_weighted": metrics.get("f1_weighted_mean"),
            "f1_macro": metrics.get("f1_macro_mean"),
            "qwk": metrics.get("kappa_qw_mean"),
            "auc_ovr": metrics.get("auc_ovr_mean"),
        },
        "refit_full_sample_for_simulator": True,
        "proposito": "simulacion_exploratoria_no_causal",
    }
    (MODEL_DIR / "model_metadata_5niveles.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    importance.to_csv(
        TABLES_DIR / "feature_importance_latest.csv",
        index=False,
        encoding="utf-8-sig",
    )
    schema.to_csv(
        TABLES_DIR / "simulator_feature_schema.csv",
        index=False,
        encoding="utf-8-sig",
    )
    interpretation.to_csv(
        TABLES_DIR / "model_interpretation_rules.csv",
        index=False,
        encoding="utf-8-sig",
    )


def choose_best_3_model(summary_3: pd.DataFrame) -> str:
    candidates = summary_3[summary_3["model"].isin(DASHBOARD_MODELS)].copy()
    if candidates.empty:
        raise ValueError("No hay modelos válidos en la corrida de 3 niveles.")
    candidates["f1_weighted_mean"] = pd.to_numeric(
        candidates["f1_weighted_mean"], errors="coerce"
    )
    return str(
        candidates.sort_values("f1_weighted_mean", ascending=False).iloc[0]["model"]
    )


def main() -> None:
    args = parse_args()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    run_5 = resolve_run(args.run_5, "5", args.mode)
    run_3 = resolve_run(args.run_3, "3", args.mode)
    summary_5, seed_5 = load_run_metrics(run_5)
    summary_3, seed_3 = load_run_metrics(run_3)

    data_path = resolve_data()
    df = read_csv(data_path)

    summary_dashboard = build_summary(summary_5, summary_3)
    seed_dashboard = build_seed_table(seed_5, seed_3)

    best_3_model = choose_best_3_model(summary_3)
    cm_5 = build_confusion_artifact(
        df,
        run_5,
        target="5",
        model_name="random_forest",
    )
    cm_3 = build_confusion_artifact(
        df,
        run_3,
        target="3",
        model_name=best_3_model,
    )

    summary_dashboard.to_csv(
        TABLES_DIR / "model_metrics_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    seed_dashboard.to_csv(
        TABLES_DIR / "model_metrics_by_seed_dashboard.csv",
        index=False,
        encoding="utf-8-sig",
    )
    cm_5.to_csv(
        TABLES_DIR / "confusion_matrix_5_levels.csv",
        index=False,
        encoding="utf-8-sig",
    )
    cm_3.to_csv(
        TABLES_DIR / "confusion_matrix_3_levels.csv",
        index=False,
        encoding="utf-8-sig",
    )

    build_simulator_artifacts(df, run_5, summary_5)

    manifest = {
        "mode": args.mode,
        "run_5": run_5.name,
        "run_3": run_3.name,
        "main_model_5": "random_forest",
        "best_model_3": best_3_model,
        "data": str(data_path.relative_to(ROOT)),
    }
    (TABLES_DIR / "model_dashboard_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n[OK] Artefactos del módulo Modelos predictivos generados.")
    print(f"[OK] Corrida principal 5 niveles: {run_5.name}")
    print(f"[OK] Corrida complementaria 3 niveles: {run_3.name}")
    print(f"[OK] Modelo matriz 3 niveles: {MODEL_LABELS[best_3_model]}")
    print(f"[OK] Tablas: {TABLES_DIR}")
    print(f"[OK] Modelo del simulador: {MODEL_DIR}")


if __name__ == "__main__":
    main()
