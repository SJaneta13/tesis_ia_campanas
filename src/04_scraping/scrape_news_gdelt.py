# src/04_scraping/scrape_news_gdelt.py
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import time
import json
import requests
import pandas as pd

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"

ECUADOR_MEDIA_DOMAINS = [
    # Principales medios/portales ecuatorianos (puedes ajustar)
    "eluniverso.com",
    "elcomercio.com",
    "primicias.ec",
    "expreso.ec",
    "lahora.com.ec",
    "teleamazonas.com",
    "ecuavisa.com",
    "extra.ec",
    "metroecuador.com.ec",
]


def build_queries(country: str = "Ecuador") -> list[str]:
    """
    Queries alineadas a tu tesis: actores + instituciones + eventos + fenómenos IA/desinformación.
    Nota: aquí NO forzamos domain: ni language: en la query para evitar depender del parser;
          filtramos después en Pandas (más estable y reproducible).
    """
    base_geo = country

    actor_queries = [
        f'("Daniel Noboa" OR Noboa) {base_geo}',
        f'("Luisa González" OR "Luisa Gonzalez") {base_geo}',
        f'("RC5" OR "Revolución Ciudadana" OR "Revolucion Ciudadana") {base_geo}',
    ]

    institutions_events = [
        f'(CNE OR "Consejo Nacional Electoral") {base_geo}',
        f'(TCE OR "Tribunal Contencioso Electoral") {base_geo}',
        f'("debate" OR "debate presidencial") {base_geo}',
        f'("segunda vuelta" OR balotaje OR runoff) {base_geo}',
        f'(escrutinio OR "actas" OR "resultados electorales") {base_geo}',
    ]

    digital_ia_risks = [
        f'("inteligencia artificial" OR IA OR deepfake OR "deep fake") {base_geo}',
        f'(bots OR bot OR "cuentas falsas" OR "coordinated") {base_geo}',
        f'(desinformación OR desinformacion OR "fake news" OR "misinformation" OR "disinformation") {base_geo}',
        f'(algoritmo OR algoritmos OR "microsegmentación" OR microsegmentacion OR "targeted ads") {base_geo}',
    ]

    elections_general = [
        f'("elecciones" OR "campaña" OR electoral OR "campaña digital" OR "redes sociales") {base_geo} 2025',
    ]

    return actor_queries + institutions_events + digital_ia_risks + elections_general


def fetch_gdelt_paged(
    query: str,
    start: str,
    end: str,
    pages: int = 6,
    page_size: int = 250,
    sleep_s: float = 1.0,
    timeout_s: int = 60,
) -> pd.DataFrame:
    all_rows: list[pd.DataFrame] = []

    for p in range(pages):
        startrecord = p * page_size + 1
        params = {
            "query": query,
            "mode": "artlist",
            "format": "json",
            "maxrecords": page_size,
            "startrecord": startrecord,
            "startdatetime": start,
            "enddatetime": end,
        }

        try:
            r = requests.get(GDELT_DOC_API, params=params, timeout=timeout_s)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"[WARN] Error request (page={p+1}) query='{query[:70]}...': {e}")
            break

        articles = data.get("articles", []) or []
        if not articles:
            break

        df = pd.json_normalize(articles)

        # columnas típicas de GDELT DOC
        keep = [c for c in ["url", "title", "seendate", "domain", "language", "sourceCountry"] if c in df.columns]
        if not keep:
            print(f"[WARN] Respuesta sin columnas esperadas (page={p+1}) query='{query[:70]}...'")
            break

        df = df[keep].copy()

        if "seendate" in df.columns:
            df = df.rename(columns={"seendate": "published_at"})
        if "sourceCountry" not in df.columns:
            df["sourceCountry"] = None

        df["query"] = query
        df["platform"] = "news_gdelt"
        all_rows.append(df)

        time.sleep(sleep_s)

    if not all_rows:
        return pd.DataFrame()

    out = pd.concat(all_rows, ignore_index=True)

    # Dedup dentro de la query
    if "url" in out.columns:
        out = out.drop_duplicates(subset=["url"]).reset_index(drop=True)

    return out


def apply_filters(
    df: pd.DataFrame,
    lang: str | None = None,
    source_country: str | None = None,
    only_ec_media: bool = False,
) -> pd.DataFrame:
    """
    Filtra el universo para aumentar validez analítica:
    - lang: "EN" o "ES" (o None = no filtrar)
    - source_country: "EC" para medios ecuatorianos (según GDELT)
    - only_ec_media: filtra por dominios ecuatorianos conocidos (whitelist)
    """
    if df.empty:
        return df

    out = df.copy()

    # normaliza strings
    for c in ["language", "domain", "sourceCountry"]:
        if c in out.columns:
            out[c] = out[c].astype(str).str.strip()

    if lang:
        lang = lang.upper()
        if "language" in out.columns:
            lang_map = {
                "ES": ["SPANISH"],
                "EN": ["ENGLISH"],
            }
            targets = lang_map.get(lang, [lang])
            lang_series = out["language"].astype(str).str.upper().str.strip()
            out = out[lang_series.isin(targets)].copy()

    if source_country:
        source_country = source_country.upper()
        if "sourceCountry" in out.columns:
            out = out[out["sourceCountry"].str.upper() == source_country].copy()

    if only_ec_media and "domain" in out.columns:
        domains = set([d.lower() for d in ECUADOR_MEDIA_DOMAINS])
        out = out[out["domain"].str.lower().isin(domains)].copy()

    # dedup final por url
    if "url" in out.columns:
        out = out.drop_duplicates(subset=["url"]).reset_index(drop=True)

    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", type=str, default="data/external/news_gdelt")
    p.add_argument("--start", type=str, default="20250201000000")
    p.add_argument("--end", type=str, default="20250501000000")
    p.add_argument("--pages", type=int, default=6)
    p.add_argument("--page-size", type=int, default=250)
    p.add_argument("--country", type=str, default="Ecuador")
    p.add_argument("--sleep", type=float, default=1.0)

    # ✅ NUEVOS: filtros que aportan a tu tesis
    p.add_argument("--lang", type=str, default="", help="Filtrar por idioma: EN o ES. Vacío = sin filtro.")
    p.add_argument("--source-country", type=str, default="", help="Filtrar por país de la fuente (ej: EC). Vacío = sin filtro.")
    p.add_argument("--only-ec-media", action="store_true", help="Filtrar por lista blanca de dominios ecuatorianos.")

    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    queries = build_queries(args.country)

    per_query_counts: dict[str, int] = {}
    all_df: list[pd.DataFrame] = []

    for q in queries:
        df_q = fetch_gdelt_paged(
            q,
            args.start,
            args.end,
            pages=args.pages,
            page_size=args.page_size,
            sleep_s=args.sleep,
        )
        per_query_counts[q] = int(len(df_q))
        print(f"[OK] '{q[:70]}...' -> {len(df_q)} rows")
        all_df.append(df_q)

    df_all = pd.concat(all_df, ignore_index=True) if all_df else pd.DataFrame()

    # dedup global antes de filtrar
    if not df_all.empty and "url" in df_all.columns:
        before = len(df_all)
        df_all = df_all.drop_duplicates(subset=["url"]).reset_index(drop=True)
        print(f"[DEDUP pre-filter] {before} → {len(df_all)} unique URLs")

    # aplica filtros (si se indicaron)
    lang = args.lang.strip() or None
    source_country = args.source_country.strip() or None
    df_all_f = apply_filters(df_all, lang=lang, source_country=source_country, only_ec_media=args.only_ec_media)

    if df_all_f.empty:
        print("[WARN] 0 resultados tras filtros. Prueba sin --lang/--source-country o quita --only-ec-media.")
        return

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # nombre del archivo incluye filtros para trazabilidad
    suffix = []
    if lang: suffix.append(f"lang{lang}")
    if source_country: suffix.append(f"src{source_country}")
    if args.only_ec_media: suffix.append("ecmedia")
    suffix = ("_" + "_".join(suffix)) if suffix else ""

    out_raw = outdir / f"news_gdelt_universe_{run_id}{suffix}.csv"
    df_all_f.to_csv(out_raw, index=False, encoding="utf-8")

    meta = {
        "run_id": run_id,
        "utc_timestamp": datetime.now(timezone.utc).isoformat(),
        "start": args.start,
        "end": args.end,
        "pages": args.pages,
        "page_size": args.page_size,
        "sleep": args.sleep,
        "country": args.country,
        "filters": {
            "lang": lang,
            "sourceCountry": source_country,
            "only_ec_media": bool(args.only_ec_media),
            "ec_media_domains": ECUADOR_MEDIA_DOMAINS if args.only_ec_media else [],
        },
        "queries": queries,
        "rows_per_query": per_query_counts,
        "n_rows_total_after_filters": int(len(df_all_f)),
        "n_unique_urls": int(df_all_f["url"].nunique()) if "url" in df_all_f.columns else int(len(df_all_f)),
        "out_file": str(out_raw),
        "columns": list(df_all_f.columns),
    }

    meta_path = outdir / f"run_{run_id}_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[DONE] universe: {out_raw} ({len(df_all_f)} rows)")
    print(f"[DONE] meta: {meta_path}")


if __name__ == "__main__":
    main()
