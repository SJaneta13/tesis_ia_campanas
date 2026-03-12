# src/06_visualization/sentiment_plots.py
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

    counts = df["sentiment_label"].value_counts()

    plt.figure()
    counts.plot(kind="bar")
    plt.title("Distribución general del sentimiento (Noticias)")
    plt.xlabel("Sentimiento")
    plt.ylabel("Número de noticias")
    plt.tight_layout()

    outfile = outdir / "sentiment_distribution.png"
    plt.savefig(outfile)
    plt.close()

    print(f"[DONE] saved: {outfile}")

if __name__ == "__main__":
    main()
