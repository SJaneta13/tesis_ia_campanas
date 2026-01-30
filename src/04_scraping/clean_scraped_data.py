# src/04_scraping/clean_scraped_data.py
from __future__ import annotations

import argparse
from pathlib import Path
import re
import pandas as pd

AI_REGEX = re.compile(
    r"\b(ia|inteligencia artificial|deepfake|deep\s*fake|bots?|desinformaci[oó]n|manipulaci[oó]n|algoritm\w*|microsegmentaci[oó]n)\b",
    re.IGNORECASE,
)

def latest_csv(folder: Path, prefix: str) -> Path:
    files = sorted(folder.glob(f"{prefix}*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No se encontraron CSVs con prefijo '{prefix}' en: {folder}")
    return files[0]

def basic_text_clean(s: str) -> str:
    s = str(s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def parse_gdelt_datetime(s: str) -> str:
    if not s or pd.isna(s):
        return ""
    s = str(s).strip()
    m = re.match(r"^(\d{8})T(\d{6})Z$", s)
    if m:
        d = m.group(1)
        t = m.group(2)
        return f"{d[0:4]}-{d[4:6]}-{d[6:8]} {t[0:2]}:{t[2:4]}:{t[4:6]}"
    return s

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--newsdir", type=str, default="data/external/news_gdelt")
    p.add_argument("--out", type=str, default="data/processed/digital_content_clean.csv")
    p.add_argument("--case-id", type=str, default="case0_universe")
    p.add_argument("--run-id", type=str, default="")

    args = p.parse_args()

    newsdir = Path(args.newsdir)
    infile = latest_csv(newsdir, "news_gdelt_enriched_")
    df = pd.read_csv(infile)

    if df.empty:
        raise FileNotFoundError(f"El archivo existe pero está vacío: {infile}")

    # asegurar columnas mínimas
    for col in ["url", "title", "published_at", "domain", "language", "query", "platform", "text"]:
        if col not in df.columns:
            df[col] = ""

    # normalización
    df["published_at"] = df["published_at"].astype(str).apply(parse_gdelt_datetime)
    df["title"] = df["title"].astype(str).apply(basic_text_clean)
    df["text"] = df["text"].astype(str).apply(basic_text_clean)

    # ✅ crea columna date (datetime real)
    df["date"] = pd.to_datetime(df["published_at"], errors="coerce")

    # etiqueta IA
    df["is_ai_related"] = df["text"].astype(str).apply(lambda s: bool(AI_REGEX.search(s)))

    # ✅ deduplicación global por url
    df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)

    run_id = args.run_id or Path(infile).stem.replace("news_gdelt_enriched_", "")
    df["case_id"] = args.case_id
    df["run_id"] = run_id
    df["stage"] = "clean"

    out = df[
        ["platform", "url", "published_at", "date", "domain", "language", "title", "text", "query", "is_ai_related"]
    ].copy()

    outpath = Path(args.out)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(outpath, index=False, encoding="utf-8")
    print(f"[DONE] clean: {outpath} ({len(out)} rows) | IA-related: {int(out['is_ai_related'].sum())}")

if __name__ == "__main__":
    main()

