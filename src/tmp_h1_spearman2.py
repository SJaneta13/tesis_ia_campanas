from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


# El archivo está dentro de src/, por eso parents[1] es la raíz del proyecto.
ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "encuestas"
    / "model_ready.csv"
)

OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "latest"
    / "tables"
    / "h1_spearman_sensitivity.csv"
)


COL_MANIP = (
    "Percepción sobre el uso de IA en campañas políticas "
    "[Los partidos pueden manipular mi opinión mediante "
    "mensajes personalizados creados con IA.]_num"
)

COL_BOTS = (
    "Percepción sobre el uso de IA en campañas políticas "
    "[La presencia de bots o cuentas falsas en redes sociales "
    "reduce mi confianza en la información política digital.]_num"
)

COL_DEEPFAKE = (
    "Percepción sobre el uso de IA en campañas políticas "
    "[La existencia de deepfakes o contenido manipulado me hace "
    "desconfiar más de las campañas políticas digitales.]_num"
)

COL_CONFIDENCE = "confianza_idx"


def fisher_ci(
    rho: float,
    n: int,
) -> tuple[float, float]:
    """
    Calcula un IC 95 % aproximado mediante
    transformación z de Fisher.
    """
    if n <= 3:
        raise ValueError(
            "Se requieren más de tres observaciones."
        )

    if not np.isfinite(rho):
        raise ValueError(
            "La correlación no es un valor numérico válido."
        )

    if abs(rho) >= 1:
        raise ValueError(
            "La transformación de Fisher requiere |rho| < 1."
        )

    z_rho = np.arctanh(rho)
    standard_error = 1 / np.sqrt(n - 3)
    z_critical = 1.959963984540054

    lower = np.tanh(
        z_rho - z_critical * standard_error
    )

    upper = np.tanh(
        z_rho + z_critical * standard_error
    )

    return float(lower), float(upper)


def calculate_spearman(
    data: pd.DataFrame,
    index_column: str,
) -> dict:
    x = data[index_column].to_numpy(
        dtype=float,
    )

    y = data[COL_CONFIDENCE].to_numpy(
        dtype=float,
    )

    if len(x) <= 3:
        raise ValueError(
            "No existen observaciones suficientes "
            "para calcular la correlación."
        )

    if np.unique(x).size < 2:
        raise ValueError(
            f"La variable {index_column} no presenta variación."
        )

    if np.unique(y).size < 2:
        raise ValueError(
            f"La variable {COL_CONFIDENCE} no presenta variación."
        )

    result = spearmanr(
        x,
        y,
        alternative="two-sided",
        nan_policy="omit",
    )

    rho = float(result.statistic)
    p_value = float(result.pvalue)
    n = int(len(x))

    ci_low, ci_high = fisher_ci(
        rho,
        n,
    )

    return {
        "n": n,
        "rho": rho,
        "p_value": p_value,
        "ci95_low": ci_low,
        "ci95_high": ci_high,
    }


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo:\n{INPUT_PATH}"
        )

    df = pd.read_csv(
        INPUT_PATH,
        encoding="utf-8-sig",
    )

    required_columns = [
        COL_MANIP,
        COL_BOTS,
        COL_DEEPFAKE,
        COL_CONFIDENCE,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            "Faltan columnas requeridas:\n- "
            + "\n- ".join(missing_columns)
        )

    # Misma muestra para ambos escenarios.
    data = (
        df[required_columns]
        .apply(pd.to_numeric, errors="coerce")
        .dropna()
        .copy()
    )

    # Índice completo: tres ítems.
    data["riesgo_ia_completo"] = data[
        [
            COL_MANIP,
            COL_BOTS,
            COL_DEEPFAKE,
        ]
    ].mean(axis=1)

    # Índice reducido: excluye bots-confianza.
    data["riesgo_ia_reducido"] = data[
        [
            COL_MANIP,
            COL_DEEPFAKE,
        ]
    ].mean(axis=1)

    complete = calculate_spearman(
        data,
        "riesgo_ia_completo",
    )

    reduced = calculate_spearman(
        data,
        "riesgo_ia_reducido",
    )

    concordance, _ = spearmanr(
        data["riesgo_ia_completo"],
        data["riesgo_ia_reducido"],
    )

    delta_rho = abs(
        reduced["rho"] - complete["rho"]
    )

    results = pd.DataFrame(
        [
            {
                "scenario": "Índice completo",
                "n_items": 3,
                **complete,
                "index_concordance": float(
                    concordance
                ),
                "delta_rho": float(delta_rho),
            },
            {
                "scenario": "Índice reducido",
                "n_items": 2,
                **reduced,
                "index_concordance": float(
                    concordance
                ),
                "delta_rho": float(delta_rho),
            },
        ]
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nRESULTADOS DE SENSIBILIDAD H1")
    print(results.to_string(index=False))

    print(
        "\nArchivo creado correctamente en:"
    )
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()