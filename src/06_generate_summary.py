import pandas as pd
import re
from pathlib import Path


def generate_keyword_summary(file_path, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(file_path, encoding="utf-8-sig")

    text_col = "content" if "content" in df.columns else "text"

    required = [text_col, "sentiment_label"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Faltan columnas requeridas: {missing}")

    df[text_col] = df[text_col].fillna("").astype(str)
    df["sentiment_label"] = (
        df["sentiment_label"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    keywords = [
        "noboa", "luisa", "fraude", "cne", "iza", "correismo",
        "voto", "elecciones", "crisis", "gobierno", "seguridad",
        "transparencia", "campaña", "ia", "bots", "deepfake",
        "desinformación"
    ]

    summary_data = []

    for kw in keywords:
        pattern = rf"\b{re.escape(kw)}\b"
        mask = df[text_col].str.contains(pattern, case=False, na=False, regex=True)
        subset = df[mask]

        count = len(subset)

        if count > 0:
            sentiment_counts = subset["sentiment_label"].value_counts().to_dict()
            top_sentiment = subset["sentiment_label"].mode()[0]

            summary_data.append({
                "Palabra clave": kw,
                "Menciones": count,
                "Sentimiento predominante": top_sentiment,
                "Positivo": sentiment_counts.get("positivo", 0),
                "Neutral": sentiment_counts.get("neutral", 0),
                "Negativo": sentiment_counts.get("negativo", 0),
            })

    summary_df = pd.DataFrame(summary_data)

    if not summary_df.empty:
        summary_df = summary_df.sort_values(by="Menciones", ascending=False)

    summary_df.to_csv(
        output_path.with_suffix(".csv"),
        index=False,
        encoding="utf-8-sig"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Resumen de análisis de sentimiento por palabras clave\n\n")
        f.write(f"**Total de registros analizados:** {len(df)}\n\n")

        f.write("## Distribución general de sentimientos\n")
        gen_counts = df["sentiment_label"].value_counts()

        for label, count in gen_counts.items():
            pct = round(count / len(df) * 100, 2)
            f.write(f"- **{label.capitalize()}:** {count} ({pct}%)\n")

        f.write("\n## Análisis por términos relevantes\n\n")

        if summary_df.empty:
            f.write("No se encontraron menciones para las palabras clave definidas.\n")
        else:
            f.write(summary_df.to_markdown(index=False))

        f.write(
            "\n\n---\n"
            "*Reporte generado como evidencia complementaria del análisis exploratorio "
            "de contenido digital.*"
        )

    print(f"Reporte generado exitosamente en: {output_path}")


if __name__ == "__main__":
    input_csv = "outputs/latest/tables/news_sentiment_scored.csv"
    output_md = "outputs/latest/tables/resumen_sentimiento_keywords.md"
    generate_keyword_summary(input_csv, output_md)