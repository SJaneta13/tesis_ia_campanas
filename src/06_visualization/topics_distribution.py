# src/06_visualization/topics_distribution.py
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--topics-file", required=True)
    p.add_argument("--outdir", default="outputs/text_analysis/plots")
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.topics_file)

    if "dominant_topic" not in df.columns:
        raise ValueError("El archivo debe tener la columna 'dominant_topic'. Usa el output news_topics_docs.csv.")

    counts = df["dominant_topic"].value_counts().sort_index()

    plt.figure()
    counts.plot(kind="bar")
    plt.title("Distribución de tópicos (LDA) por documento")
    plt.xlabel("Tópico dominante")
    plt.ylabel("Número de noticias")
    plt.tight_layout()

    out = outdir / "topics_distribution.png"
    plt.savefig(out, dpi=200)
    print(f"[DONE] saved: {out}")

if __name__ == "__main__":
    main()

