from pathlib import Path
import pandas as pd

def fmt(mean, std, digits=3):
    if pd.isna(mean):
        return ""
    if pd.isna(std):
        return f"{mean:.{digits}f}"
    return f"{mean:.{digits}f} ± {std:.{digits}f}"

def main():
    RUNS_DIR = Path("outputs") / "runs"
    runs = sorted(RUNS_DIR.glob("run_*"))
    if not runs:
        raise FileNotFoundError("No hay runs en outputs/runs.")

    last_run_dir = runs[-1]
    tables_dir = last_run_dir / "tables"
    ordinal_dir = last_run_dir / "ordinal"

    # --- sklearn summary ---
    sklearn_files = sorted(tables_dir.glob("metrics_run_*.csv"))
    if not sklearn_files:
        raise FileNotFoundError(f"No encontré metrics_run_*.csv en {tables_dir}")
    df_sklearn = pd.read_csv(sklearn_files[-1])

    # --- ordinal summary ---
    ordinal_file = ordinal_dir / "metrics.csv"
    if not ordinal_file.exists():
        raise FileNotFoundError(f"No encontré {ordinal_file}. Ejecuta 03a_ordinal_logit.py primero.")
    df_ord = pd.read_csv(ordinal_file)


    # Detecta automáticamente si este run sklearn fue 3 clases o 5 niveles
    if (df_sklearn["target"] == "confianza_3").any():
        target_sklearn = "confianza_3"
        target_ordinal = "ordinal_logit_3clases"
    else:
        target_sklearn = "confianza_idx_round"
        target_ordinal = "ordinal_logit_5niveles"

    # Filtrar 3 modelos
    keep_models = ["random_forest", "svm_rbf"]
    df_s = df_sklearn[(df_sklearn["target"] == target_sklearn) & (df_sklearn["model"].isin(keep_models))].copy()
    df_o = df_ord[df_ord["target"] == target_ordinal].copy()
    df_o["model"] = "ordinal_logit"

    # Normalizar columnas esperadas
    def pick_cols(df):
        return df[[
            "model",
            "accuracy_mean","accuracy_std",
            "f1_weighted_mean","f1_weighted_std",
            "kappa_qw_mean","kappa_qw_std",
            "mae_ordinal_mean","mae_ordinal_std",
            "auc_ovr_mean","auc_ovr_std",
            "time_seconds_mean","time_seconds_std",
        ]].copy()

    df_s2 = pick_cols(df_s)
    df_o2 = pick_cols(df_o)

    df_all = pd.concat([df_o2, df_s2], ignore_index=True)

    # Orden fijo
    order = pd.CategoricalDtype(["ordinal_logit", "random_forest", "svm_rbf"], ordered=True)
    df_all["model"] = df_all["model"].astype(order)
    df_all = df_all.sort_values("model")

    # Aviso si falta alguno
    expected = set(["ordinal_logit", "random_forest", "svm_rbf"])
    found = set(df_all["model"].astype(str).tolist())
    missing = expected - found
    if missing:
        print("⚠️ Modelos faltantes en este run:", sorted(missing))

    interpret = {
        "ordinal_logit": "Alta (OR + IC95%)",
        "random_forest": "Media (importancias)",
        "svm_rbf": "Baja (caja negra)",
    }

    out = pd.DataFrame({
        "Modelo": df_all["model"],
        "Accuracy": [fmt(m,s) for m,s in zip(df_all["accuracy_mean"], df_all["accuracy_std"])],
        "F1_weighted": [fmt(m,s) for m,s in zip(df_all["f1_weighted_mean"], df_all["f1_weighted_std"])],
        "QWK": [fmt(m,s) for m,s in zip(df_all["kappa_qw_mean"], df_all["kappa_qw_std"])],
        "MAE_ordinal": [fmt(m,s) for m,s in zip(df_all["mae_ordinal_mean"], df_all["mae_ordinal_std"])],
        "AUC_OVR": [fmt(m,s) for m,s in zip(df_all["auc_ovr_mean"], df_all["auc_ovr_std"])],
        "Tiempo(s)": [fmt(m,s, digits=1) for m,s in zip(df_all["time_seconds_mean"], df_all["time_seconds_std"])],
        "Interpretabilidad": [interpret.get(x, "") for x in df_all["model"]],
    })

    out_path = tables_dir / f"model_comparison_{target_sklearn}.csv"
    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print("Tabla comparativa guardada en:", out_path)

    # También imprime en consola
    print(out)

if __name__ == "__main__":
    main()