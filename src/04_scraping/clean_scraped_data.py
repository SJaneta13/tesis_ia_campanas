from __future__ import annotations

import argparse
from pathlib import Path
import re
import json
import ast
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

# ======= TU LÓGICA (GDELT) - SE MANTIENE =======
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

# ======= APORTES DE CRISTIAN (NORMALIZACIÓN SOCIAL) - SE INTEGRA =======
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def _safe_parse(val):
    """Parsea valores JSON o ast de manera segura."""
    if isinstance(val, dict):
        return val
    if not isinstance(val, str):
        return {}
    try:
        return json.loads(val)
    except Exception:
        try:
            return ast.literal_eval(val)
        except Exception:
            return {}

def _fill_numeric_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Rellena columnas numéricas (likes, shares, comments) con valores por defecto."""
    for col in ["likes", "shares", "comments"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df

def _update_stats_from_dict(df: pd.DataFrame) -> pd.DataFrame:
    """Actualiza métricas de engagement desde columna 'stats' si existe."""
    if "stats" not in df.columns:
        return df

    stats = df["stats"].map(_safe_parse)
    if "likes" in df.columns:
        df["likes"] = df["likes"].mask(
            df["likes"] == 0,
            stats.map(lambda x: x.get("diggCount") or x.get("likeCount") or 0),
        )
    if "shares" in df.columns:
        df["shares"] = df["shares"].mask(
            df["shares"] == 0,
            stats.map(lambda x: x.get("shareCount") or x.get("sharesCount") or 0),
        )
    if "comments" in df.columns:
        df["comments"] = df["comments"].mask(
            df["comments"] == 0,
            stats.map(lambda x: x.get("commentCount") or x.get("commentsCount") or 0),
        )
    return df

def _ensure_required_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Asegura que las columnas requeridas existan."""
    for col in ["user", "content", "source_url", "date"]:
        if col not in df.columns:
            df[col] = ""
    return df

def _extract_nested_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Extrae campos anidados como 'author.unique_id' si existen."""
    if "author" in df.columns and (df["user"].isna() | (df["user"] == "")).any():
        authors = df["author"].map(_safe_parse)
        df["user"] = df["user"].mask(
            df["user"] == "",
            authors.map(lambda x: x.get("username") or x.get("uniqueId") or x.get("unique_id") or ""),
        )
    if "authorMeta" in df.columns and (df["user"].isna() | (df["user"] == "")).any():
        meta = df["authorMeta"].map(_safe_parse)
        df["user"] = df["user"].mask(
            df["user"] == "",
            meta.map(lambda x: x.get("name") or x.get("uniqueId") or ""),
        )
    return df

def normalize_df(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    col_map = {
        "date": "date",
        "created_time": "date",
        "timestamp": "date",
        "createTime": "date",
        "create_time": "date",
        "createdAt": "date",
        "createTimeISO": "date",
        "user": "user",
        "username": "user",
        "authorUsername": "user",
        "authorName": "user",
        "authorMeta.name": "user",
        "unique_id": "user",
        "uniqueId": "user",
        "pageName": "user",
        "pageId": "user",
        "content": "content",
        "message": "content",
        "text": "content",
        "caption": "content",
        "desc": "content",
        "title": "content",
        "likes": "likes",
        "likesCount": "likes",
        "reactionsCount": "likes",
        "diggCount": "likes",
        "digg_count": "likes",
        "shares": "shares",
        "retweets": "shares",
        "sharesCount": "shares",
        "shareCount": "shares",
        "share_count": "shares",
        "commentsCount": "comments",
        "commentCount": "comments",
        "comment_count": "comments",
        "source_url": "source_url",
        "permalink_url": "source_url",
        "url": "source_url",
        "postUrl": "source_url",
        "play": "source_url",
        "webVideoUrl": "source_url",
    }

    df = df.rename(columns=col_map)
    df = df.loc[:, ~df.columns.duplicated()]
    df["platform"] = platform

    df = _fill_numeric_cols(df)
    df = _update_stats_from_dict(df)
    df = _ensure_required_cols(df)
    df = _extract_nested_fields(df)

    df["content"] = df["content"].map(clean_text)

    # Filtrar si después de limpiar no queda nada de texto
    df = df[df["content"].str.len() > 0]

    df = df.drop_duplicates(subset=["content", "date", "user"])

    keep_cols = [
        "platform",
        "date",
        "user",
        "content",
        "likes",
        "shares",
        "comments",
        "source_url",
    ]
    return df[keep_cols]

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

    # crea columna date (datetime real)
    df["date"] = pd.to_datetime(df["published_at"], errors="coerce")

    # etiqueta IA
    df["is_ai_related"] = df["text"].astype(str).apply(lambda s: bool(AI_REGEX.search(s)))

    # deduplicación global por url
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
