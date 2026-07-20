from pathlib import Path
import pandas as pd

ROOT = Path(".")

files = {
    "Noticias ES": ROOT / "outputs/text_analysis/case1_es/news_sentiment_scored.csv",
    "Noticias EN": ROOT / "outputs/text_analysis/case2_en/news_sentiment_scored.csv",
    "Medios EC": ROOT / "outputs/text_analysis/case3_ec_media/news_sentiment_scored.csv",
    "X/Twitter": ROOT / "outputs/text_analysis/social_x/social_sentiment_scored.csv",
    "Social limpio": ROOT / "data/processed/social_clean.csv",
}

rows = []

for name, path in files.items():
    if not path.exists():
        rows.append({
            "fuente": name,
            "archivo": str(path),
            "existe": False,
            "registros": 0,
            "fecha_min": None,
            "fecha_max": None,
            "sentimiento_valido": 0,
        })
        continue

    df = pd.read_csv(path, encoding="utf-8-sig")

    date_col = next(
        (c for c in ["date", "published_at", "created_time"] if c in df.columns),
        None,
    )

    label_col = next(
        (
            c for c in [
                "sentiment_label",
                "sentiment_label_std",
                "sentiment_raw_label",
            ]
            if c in df.columns
        ),
        None,
    )

    dates = (
        pd.to_datetime(df[date_col], errors="coerce")
        if date_col
        else pd.Series(dtype="datetime64[ns]")
    )

    valid_sentiment = (
        df[label_col].notna().sum()
        if label_col
        else 0
    )

    rows.append({
        "fuente": name,
        "archivo": str(path),
        "existe": True,
        "registros": len(df),
        "fecha_min": dates.min() if not dates.empty else None,
        "fecha_max": dates.max() if not dates.empty else None,
        "sentimiento_valido": int(valid_sentiment),
    })

summary = pd.DataFrame(rows)

print("\nRESUMEN DE CORPUS")
print(summary.to_string(index=False))

print("\nTOTAL CARGADO POR EL DASHBOARD:")
dashboard_total = summary.loc[
    summary["fuente"].isin(
        ["Noticias ES", "Noticias EN", "Medios EC", "X/Twitter"]
    ),
    "registros",
].sum()

print(int(dashboard_total))

social_path = files["Social limpio"]

if social_path.exists():
    social = pd.read_csv(social_path, encoding="utf-8-sig")

    if "platform" in social.columns:
        print("\nSOCIAL_CLEAN POR PLATAFORMA")
        print(social["platform"].value_counts(dropna=False))