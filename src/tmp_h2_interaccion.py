from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf


INPUT_PATH = Path("data/processed/encuestas/model_ready.csv")
OUTPUT_DIR = Path("outputs/hypotheses/h2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COL_MANIP = (
    "Percepción sobre el uso de IA en campañas políticas "
    "[Los partidos pueden manipular mi opinión mediante mensajes personalizados creados con IA.]_num"
)

COL_BOTS = (
    "Percepción sobre el uso de IA en campañas políticas "
    "[La presencia de bots o cuentas falsas en redes sociales reduce mi confianza "
    "en la información política digital.]_num"
)

COL_DEEPFAKE = (
    "Percepción sobre el uso de IA en campañas políticas "
    "[La existencia de deepfakes o contenido manipulado me hace desconfiar más "
    "de las campañas políticas digitales.]_num"
)

COL_VERIFY = (
    "¿Realiza alguna verificación (chequea fuentes, busca noticias, consulta otras personas) "
    "de la información política digital antes de compartirla?"
)

COL_CONFIDENCE = "confianza_idx"


def main() -> None:
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

    required = [
        COL_MANIP,
        COL_BOTS,
        COL_DEEPFAKE,
        COL_VERIFY,
        COL_CONFIDENCE,
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise KeyError(f"Faltan columnas requeridas: {missing}")

    data = df[required].dropna().copy()

    # Índice principal de riesgo percibido por IA
    data["riesgo_ia"] = data[
        [COL_MANIP, COL_BOTS, COL_DEEPFAKE]
    ].mean(axis=1)

    # Agrupación de verificación
    verify_map = {
        "Nunca": "Baja",
        "Rara vez": "Baja",
        "A veces": "Media",
        "Siempre": "Alta",
    }

    data["verificacion_nivel"] = data[COL_VERIFY].map(verify_map)

    if data["verificacion_nivel"].isna().any():
        invalid = data.loc[
            data["verificacion_nivel"].isna(), COL_VERIFY
        ].unique()
        raise ValueError(f"Categorías de verificación no reconocidas: {invalid}")

    verify_num_map = {
        "Baja": 1,
        "Media": 2,
        "Alta": 3,
    }

    data["verificacion_num"] = (
        data["verificacion_nivel"]
        .map(verify_num_map)
        .astype(int)
    )

    # Modelos simples por grupo
    group_rows = []

    for level in ["Baja", "Media", "Alta"]:
        subset = data[data["verificacion_nivel"] == level].copy()

        model = smf.ols(
            "confianza_idx ~ riesgo_ia",
            data=subset,
        ).fit()

        ci = model.conf_int().loc["riesgo_ia"]

        group_rows.append(
            {
                "nivel_verificacion": level,
                "n": len(subset),
                "pendiente": model.params["riesgo_ia"],
                "error_estandar": model.bse["riesgo_ia"],
                "ic95_inferior": ci[0],
                "ic95_superior": ci[1],
                "p_valor": model.pvalues["riesgo_ia"],
                "r_cuadrado": model.rsquared,
            }
        )

    group_results = pd.DataFrame(group_rows)

    # Modelo global con interacción ordinal
    interaction_model = smf.ols(
        "confianza_idx ~ riesgo_ia * verificacion_num",
        data=data,
    ).fit()

    interaction_term = "riesgo_ia:verificacion_num"
    interaction_ci = interaction_model.conf_int().loc[interaction_term]

    interaction_results = pd.DataFrame(
        [
            {
                "n_total": len(data),
                "coef_interaccion": interaction_model.params[interaction_term],
                "error_estandar": interaction_model.bse[interaction_term],
                "ic95_inferior": interaction_ci[0],
                "ic95_superior": interaction_ci[1],
                "p_valor": interaction_model.pvalues[interaction_term],
                "r_cuadrado": interaction_model.rsquared,
                "r_cuadrado_ajustado": interaction_model.rsquared_adj,
            }
        ]
    )

    # Distribución de los grupos
    group_counts = (
        data["verificacion_nivel"]
        .value_counts()
        .reindex(["Baja", "Media", "Alta"])
        .rename_axis("nivel_verificacion")
        .reset_index(name="n")
    )

    # Guardado reproducible
    group_results.to_csv(
        OUTPUT_DIR / "h2_pendientes_por_grupo.csv",
        index=False,
        encoding="utf-8-sig",
    )

    interaction_results.to_csv(
        OUTPUT_DIR / "h2_interaccion_global.csv",
        index=False,
        encoding="utf-8-sig",
    )

    group_counts.to_csv(
        OUTPUT_DIR / "h2_distribucion_verificacion.csv",
        index=False,
        encoding="utf-8-sig",
    )

    data[
        [
            "riesgo_ia",
            "verificacion_nivel",
            "verificacion_num",
            COL_CONFIDENCE,
        ]
    ].to_csv(
        OUTPUT_DIR / "h2_dataset_analitico.csv",
        index=False,
        encoding="utf-8-sig",
    )

    summary_path = OUTPUT_DIR / "h2_resumen_modelo.txt"

    with summary_path.open("w", encoding="utf-8") as file:
        file.write("ANÁLISIS EXPLORATORIO DE H2\n")
        file.write("=" * 50 + "\n\n")
        file.write(
            "Modelo: regresión lineal exploratoria con interacción "
            "riesgo percibido × verificación informativa.\n"
        )
        file.write(
            "Variable dependiente: índice de confianza electoral 1–5, "
            "tratado como cuasicontinuo.\n\n"
        )
        file.write("PENDIENTES POR GRUPO\n")
        file.write(group_results.to_string(index=False))
        file.write("\n\nMODELO GLOBAL\n")
        file.write(interaction_model.summary().as_text())

    print("\nPendientes por grupo")
    print(group_results.round(4).to_string(index=False))

    print("\nInteracción global")
    print(interaction_results.round(4).to_string(index=False))

    print(f"\nArchivos guardados en: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()