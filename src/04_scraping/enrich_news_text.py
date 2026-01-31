# src/04_scraping/enrich_news_text.py
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    # elimina basura típica
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def fetch_url_text(url: str, timeout: int = 30) -> str | None:
    try:
        r = requests.get(
            url,
            headers={"User-Agent": UA, "Accept-Language": "es-EC,es;q=0.9,en;q=0.8"},
            timeout=timeout,
            allow_redirects=True,
        )
        if r.status_code >= 400:
            return None
        # evita binarios raros
        ctype = (r.headers.get("Content-Type") or "").lower()
        if "text/html" not in ctype and "application/xhtml+xml" not in ctype:
            return None
        return html_to_text(r.text)
    except Exception:
        return None

def latest_csv(folder: Path, prefix: str) -> Path:
    files = sorted(folder.glob(f"{prefix}*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No se encontraron CSVs con prefijo '{prefix}' en: {folder}")
    return files[0]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--indir", type=str, default="data/external/news_gdelt", help="carpeta con news_gdelt_universe_*.csv")
    p.add_argument("--infile", type=str, default="", help="opcional: path directo al CSV universo")
    p.add_argument("--outdir", type=str, default="data/external/news_gdelt", help="carpeta salida")
    p.add_argument("--sleep", type=float, default=1.0, help="segundos entre requests (buena práctica)")
    p.add_argument("--max-chars", type=int, default=20000, help="recorta texto para que no pese demasiado")
    p.add_argument("--max-rows", type=int, default=0, help="0=todo; si quieres probar usa 50 o 100")
    args = p.parse_args()

    indir = Path(args.indir)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    infile = Path(args.infile) if args.infile else latest_csv(indir, "news_gdelt_universe_")
    df = pd.read_csv(infile)

    if df.empty:
        print("[WARN] CSV de entrada vacío.")
        return

    if args.max_rows and args.max_rows > 0:
        df = df.head(args.max_rows).copy()

    # si ya existe columna text, la respetamos; si no, creamos
    if "text" not in df.columns:
        df["text"] = ""

    enriched = []
    total = len(df)

    for i, row in df.iterrows():
        url = str(row.get("url", "")).strip()
        title = str(row.get("title", "")).strip()

        txt = None
        if url and url.startswith("http"):
            txt = fetch_url_text(url)

        # fallback: si no pudimos extraer, al menos título
        if not txt:
            txt = title

        txt = (txt or "").strip()
        if args.max_chars and len(txt) > args.max_chars:
            txt = txt[: args.max_chars]

        row_out = row.to_dict()
        row_out["text"] = txt
        enriched.append(row_out)

        if (len(enriched) % 25) == 0:
            print(f"[PROGRESS] {len(enriched)}/{total}")

        time.sleep(args.sleep)

    df_out = pd.DataFrame(enriched)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    outfile = outdir / f"news_gdelt_enriched_{run_id}.csv"
    df_out.to_csv(outfile, index=False, encoding="utf-8")
    print(f"[DONE] enriched: {outfile} ({len(df_out)} rows)")

if __name__ == "__main__":
    main()
