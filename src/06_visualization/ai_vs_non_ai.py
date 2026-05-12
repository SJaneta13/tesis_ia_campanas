# src/06_visualization/ai_vs_non_ai.py
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--outdir", default="outputs/visualization")
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)

    required = ["is_ai_related", "sentiment_label"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise KeyError(f"Faltan columnas requeridas: {missing}")

    ai = df[df["is_ai_related"] == True]["sentiment_label"].value_counts()
    non_ai = df[df["is_ai_related"] == False]["sentiment_label"].value_counts()

    plot_df = pd.DataFrame({
        "IA": ai,
        "No IA": non_ai
    }).fillna(0)

    plot_df.plot(kind="bar")
    plt.title("Sentimiento: Noticias con IA vs sin IA")
    plt.xlabel("Sentimiento")
    plt.ylabel("Número de noticias")
    plt.tight_layout()

    outfile = outdir / "ai_vs_non_ai_sentiment.png"
    plt.savefig(outfile)
    plt.close()

    print(f"[DONE] saved: {outfile}")

if __name__ == "__main__":
    main()
