from pathlib import Path

import pandas as pd


# =========================================================
# Configuración
# =========================================================
INPUT_PATH = Path("data/processed/social_clean.csv")
OUTPUT_DIR = Path("outputs/audits/social_dates")

START_DATE = pd.Timestamp("2025-02-01", tz="UTC")
END_DATE = pd.Timestamp("2025-05-01", tz="UTC")


def normalize_platform(series: pd.Series) -> pd.Series:
    """Normaliza el nombre de plataforma."""
    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .replace(
            {
                "twitter": "x",
                "x/twitter": "x",
                "facebook.com": "facebook",
                "tiktok.com": "tiktok",
            }
        )
    )


def recover_facebook_unix_dates(
    df: pd.DataFrame,
    platform: pd.Series,
) -> pd.Series:
    """
    Recupera fechas de Facebook que fueron interpretadas como nanosegundos
    desde el epoch de 1970, cuando el valor original correspondía a segundos Unix.

    Ejemplo:
        1970-01-01 00:00:01.745950044+00:00

    El entero interno 1 745 950 044 se reinterpreta como segundos Unix,
    produciendo una fecha de 2025.
    """
    years = df["date_validated"].dt.year

    recovery_mask = (
        platform.eq("facebook")
        & df["date_validated"].notna()
        & years.eq(1970)
    )

    recoverable_count = int(recovery_mask.sum())

    print(
        "\nFechas Facebook potencialmente recuperables:",
        recoverable_count,
    )

    if recoverable_count == 0:
        return recovery_mask

    # El valor interno está almacenado en nanosegundos.
    # Ese entero corresponde al timestamp Unix original en segundos.
    unix_seconds = (
        df.loc[recovery_mask, "date_validated"]
        .astype("int64")
    )

    recovered_dates = pd.to_datetime(
        unix_seconds,
        unit="s",
        errors="coerce",
        utc=True,
    )

    df.loc[
        recovery_mask,
        "date_validated",
    ] = recovered_dates

    df.loc[
        recovery_mask,
        "date_validation_method",
    ] = "unix_segundos_recuperado"

    df.loc[
        recovery_mask,
        "date_validation_status",
    ] = "fecha_recuperada"

    return recovery_mask


def build_summaries(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Construye los resúmenes por estado y por plataforma."""
    validation_summary = (
        df.groupby(
            [
                "platform",
                "date_validation_status",
                "date_validation_method",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="registros")
        .sort_values(
            [
                "platform",
                "date_validation_status",
                "date_validation_method",
            ]
        )
        .reset_index(drop=True)
    )

    platform_summary = (
        df.groupby(
            "platform",
            dropna=False,
        )
        .agg(
            registros=("platform", "size"),
            fechas_validas=(
                "date_validated",
                lambda values: int(values.notna().sum()),
            ),
            registros_en_periodo=(
                "in_analysis_period",
                lambda values: int(values.sum()),
            ),
            fecha_min=("date_validated", "min"),
            fecha_max=("date_validated", "max"),
        )
        .reset_index()
        .sort_values("platform")
        .reset_index(drop=True)
    )

    return validation_summary, platform_summary


def main() -> None:
    # =====================================================
    # 1. Validación de entrada
    # =====================================================
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {INPUT_PATH.resolve()}"
        )

    try:
        df = pd.read_csv(
            INPUT_PATH,
            encoding="utf-8-sig",
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            INPUT_PATH,
            encoding="latin1",
        )

    required_columns = {
        "platform",
        "date",
        "content",
        "source_url",
    }

    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        raise KeyError(
            "Faltan columnas obligatorias en social_clean.csv: "
            f"{sorted(missing_columns)}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\nArchivo analizado:", INPUT_PATH)
    print("Registros totales:", len(df))

    # =====================================================
    # 2. Normalización de plataforma
    # =====================================================
    df["platform_raw"] = df["platform"].astype("string")
    df["platform"] = normalize_platform(df["platform"])

    platform = df["platform"]

    # =====================================================
    # 3. Conservación y conversión inicial de fecha
    # =====================================================
    df["date_raw"] = (
        df["date"]
        .astype("string")
        .str.strip()
    )

    df["date_validated"] = pd.to_datetime(
        df["date_raw"],
        errors="coerce",
        utc=True,
    )

    # Estado inicial según disponibilidad de fecha.
    df["date_validation_method"] = "metadato_directo"
    df["date_validation_status"] = "fecha_disponible"

    no_initial_date = df["date_validated"].isna()

    df.loc[
        no_initial_date,
        "date_validation_method",
    ] = "sin_metadato_fecha"

    df.loc[
        no_initial_date,
        "date_validation_status",
    ] = "sin_fecha_pendiente"

    # =====================================================
    # 4. Recuperación de fechas Facebook
    # =====================================================
    recovery_mask = recover_facebook_unix_dates(
        df,
        platform,
    )

    recovered_valid = (
        recovery_mask
        & df["date_validated"].notna()
    )

    recovered_failed = (
        recovery_mask
        & df["date_validated"].isna()
    )

    df.loc[
        recovered_failed,
        "date_validation_method",
    ] = "unix_segundos_no_recuperable"

    df.loc[
        recovered_failed,
        "date_validation_status",
    ] = "sin_fecha_pendiente"

    print(
        "Fechas Facebook recuperadas correctamente:",
        int(recovered_valid.sum()),
    )

    # =====================================================
    # 5. Clasificación de la ventana temporal
    # =====================================================
    valid_date = df["date_validated"].notna()

    in_period = (
        valid_date
        & df["date_validated"].ge(START_DATE)
        & df["date_validated"].lt(END_DATE)
    )

    outside_period = (
        valid_date
        & ~in_period
    )

    missing_date = df["date_validated"].isna()

    df.loc[
        in_period,
        "date_validation_status",
    ] = "validado_en_periodo"

    df.loc[
        outside_period,
        "date_validation_status",
    ] = "fuera_del_periodo"

    df.loc[
        missing_date,
        "date_validation_status",
    ] = "sin_fecha_pendiente"

    df.loc[
        missing_date
        & df["date_validation_method"].eq("metadato_directo"),
        "date_validation_method",
    ] = "sin_metadato_fecha"

    df["in_analysis_period"] = in_period.astype(bool)

    # =====================================================
    # 6. Controles de consistencia
    # =====================================================
    df["validation_observation"] = ""

    df.loc[
        platform.eq("x")
        & outside_period,
        "validation_observation",
    ] = "Publicación con fecha válida, pero fuera de febrero-abril de 2025."

    df.loc[
        platform.eq("facebook")
        & missing_date,
        "validation_observation",
    ] = "Registro sin fecha individual; requiere evidencia documental o revisión manual."

    df.loc[
        platform.eq("tiktok")
        & missing_date,
        "validation_observation",
    ] = "Registro sin fecha utilizable; requiere revisión del metadato original."

    df.loc[
        in_period,
        "validation_observation",
    ] = "Registro temporalmente válido para la ventana principal del estudio."

    # =====================================================
    # 7. Resúmenes
    # =====================================================
    validation_summary, platform_summary = build_summaries(df)

    # =====================================================
    # 8. Registros pendientes de revisión
    # =====================================================
    pending = df[
        df["date_validation_status"].eq(
            "sin_fecha_pendiente"
        )
    ].copy()

    pending["manual_validated_date"] = ""
    pending["manual_validation_method"] = ""
    pending["manual_evidence"] = ""
    pending["manual_validation_status"] = "pendiente"
    pending["manual_observation"] = ""

    # Registros confirmados dentro del periodo.
    valid_period = df[
        df["in_analysis_period"]
    ].copy()

    # Registros fuera del periodo.
    outside = df[
        df["date_validation_status"].eq(
            "fuera_del_periodo"
        )
    ].copy()

    # =====================================================
    # 9. Guardado de resultados
    # =====================================================
    validation_path = (
        OUTPUT_DIR / "social_date_validation.csv"
    )

    summary_path = (
        OUTPUT_DIR / "social_date_validation_summary.csv"
    )

    platform_summary_path = (
        OUTPUT_DIR / "social_date_platform_summary.csv"
    )

    pending_path = (
        OUTPUT_DIR / "social_dates_pending_manual_review.csv"
    )

    valid_period_path = (
        OUTPUT_DIR / "social_records_validated_in_period.csv"
    )

    outside_path = (
        OUTPUT_DIR / "social_records_outside_period.csv"
    )

    df.to_csv(
        validation_path,
        index=False,
        encoding="utf-8-sig",
    )

    validation_summary.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig",
    )

    platform_summary.to_csv(
        platform_summary_path,
        index=False,
        encoding="utf-8-sig",
    )

    pending.to_csv(
        pending_path,
        index=False,
        encoding="utf-8-sig",
    )

    valid_period.to_csv(
        valid_period_path,
        index=False,
        encoding="utf-8-sig",
    )

    outside.to_csv(
        outside_path,
        index=False,
        encoding="utf-8-sig",
    )

    # =====================================================
    # 10. Salida en consola
    # =====================================================
    print("\n" + "=" * 90)
    print("RESUMEN POR PLATAFORMA")
    print("=" * 90)
    print(platform_summary.to_string(index=False))

    print("\n" + "=" * 90)
    print("RESUMEN POR ESTADO DE VALIDACIÓN")
    print("=" * 90)
    print(validation_summary.to_string(index=False))

    print("\n" + "=" * 90)
    print("CONTROL GENERAL")
    print("=" * 90)
    print(
        "Registros válidos dentro del periodo:",
        int(df["in_analysis_period"].sum()),
    )
    print(
        "Registros fuera del periodo:",
        int(
            df["date_validation_status"]
            .eq("fuera_del_periodo")
            .sum()
        ),
    )
    print(
        "Registros pendientes de revisión manual:",
        len(pending),
    )

    print("\nArchivos guardados:")
    print("-", validation_path)
    print("-", summary_path)
    print("-", platform_summary_path)
    print("-", pending_path)
    print("-", valid_period_path)
    print("-", outside_path)


if __name__ == "__main__":
    main()