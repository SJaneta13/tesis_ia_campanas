from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

MODEL_DIR = ROOT / "outputs" / "latest" / "models_dashboard"
TABLES_DIR = ROOT / "outputs" / "latest" / "tables"

MODEL_PATH_5 = MODEL_DIR / "simulator_best_model_5niveles.joblib"
DEFAULTS_PATH_5 = TABLES_DIR / "simulator_defaults_5niveles.json"
METADATA_PATH_5 = MODEL_DIR / "model_metadata_5niveles.json"
CLASSES_PATH_5 = MODEL_DIR / "model_classes_5niveles.json"

# Compatibilidad si todavía existen artefactos antiguos de 3 niveles.
MODEL_PATH_3 = MODEL_DIR / "simulator_best_model_3niveles.joblib"
DEFAULTS_PATH_3 = TABLES_DIR / "simulator_defaults_3niveles.json"

CLASS_ORDER_5 = ["Muy baja", "Baja", "Media", "Alta", "Muy alta"]

CLASS_COLORS = {
    "Muy baja": "#dc2626",
    "Baja": "#ea580c",
    "Media": "#d97706",
    "Alta": "#059669",
    "Muy alta": "#047857",
}


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _pretty_label(label: Any) -> str:
    text = str(label).strip()
    low = text.lower()

    if "confianza electoral" in low:
        return text

    if low in {"muy baja", "muy_baja"}:
        return "Muy baja confianza electoral"
    if low == "baja":
        return "Baja confianza electoral"
    if low in {"media", "moderada", "medio"}:
        return "Confianza media electoral"
    if low == "alta":
        return "Alta confianza electoral"
    if low in {"muy alta", "muy_alta"}:
        return "Muy alta confianza electoral"

    return f"{text} confianza electoral"


def _base_label(label: Any) -> str:
    text = str(label).replace(" confianza electoral", "").replace("Confianza ", "").strip()
    text = text.replace("electoral", "").strip()
    if text.lower() == "media":
        return "Media"
    if text.lower() == "muy baja":
        return "Muy baja"
    if text.lower() == "muy alta":
        return "Muy alta"
    return text


def _color_for_label(label: Any) -> str:
    base = _base_label(label)
    return CLASS_COLORS.get(base, "#64748b")


@st.cache_resource(show_spinner=False)
def load_simulator_model():
    """
    Carga exclusivamente el modelo real del simulador:
    Random Forest, configuración principal de 5 niveles.
    """
    if MODEL_PATH_5.exists() and DEFAULTS_PATH_5.exists():
        model = joblib.load(MODEL_PATH_5)
        defaults = _read_json(DEFAULTS_PATH_5, {})
        metadata = _read_json(METADATA_PATH_5, {})
        classes_meta = _read_json(CLASSES_PATH_5, {"classes": CLASS_ORDER_5})
        return model, defaults, metadata, classes_meta

    return None, None, None, None

def predict_simulator(values: dict) -> dict[str, Any] | None:
    """Predice una clase de confianza electoral con el pipeline entrenado.

    values contiene solo las variables modificables desde el frontend. El resto
    de columnas del modelo se completa con defaults calculados desde la muestra.
    """
    model, defaults, metadata, classes_meta = load_simulator_model()

    if model is None or defaults is None:
        return None

    row = dict(defaults)
    for key, value in values.items():
        if key in row:
            row[key] = value

    X = pd.DataFrame([row])
    pred = model.predict(X)[0]

    probabilities: dict[str, float] = {}
    probability = 0.0

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        trained_classes = list(model.classes_)
        probabilities = {str(cls): float(proba[i]) for i, cls in enumerate(trained_classes)}
        probability = probabilities.get(str(pred), float(max(proba)))

    ordered = classes_meta.get("classes") if isinstance(classes_meta, dict) else None
    if not ordered:
        ordered = CLASS_ORDER_5 if str(metadata or {}).find("5 niveles") >= 0 else list(probabilities.keys())

    distribution = []
    for cls in ordered:
        base = _base_label(cls)
        value = probabilities.get(base, probabilities.get(str(cls), 0.0))
        distribution.append(
            {
                "class": _pretty_label(base),
                "base_class": base,
                "probability": float(value),
                "color": _color_for_label(base),
            }
        )

    base_pred = _base_label(pred)
    return {
        "label": _pretty_label(base_pred),
        "base_class": base_pred,
        "probability": float(probability),
        "color": _color_for_label(base_pred),
        "distribution": distribution,
        "metadata": metadata or {},
        "uses_real_model": MODEL_PATH_5.exists(),
    }


def predict_with_trained_model(values: dict) -> tuple[str | None, float | None, str | None]:
    """Compatibilidad con versiones anteriores de modelos_predictivos.py."""
    result = predict_simulator(values)
    if result is None:
        return None, None, None
    return result["label"], result["probability"], result["color"]
