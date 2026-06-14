from __future__ import annotations

import argparse
import re
import json
import ast
from pathlib import Path
import pandas as pd


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
    for col in ["likes", "shares", "comments"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df


def _update_stats_from_dict(df: pd.DataFrame) -> pd.DataFrame:
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
    for col in ["user", "content", "source_url", "date"]:
        if col not in df.columns:
            df[col] = ""
    return df


def _extract_nested_fields(df: pd.DataFrame) -> pd.DataFrame:
    # opcional: extrae usuario desde campos anidados si existen
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
    df["source_type"] = "social_media"

    df = _fill_numeric_cols(df)
    df = _update_stats_from_dict(df)
    df = _ensure_required_cols(df)
    df = _extract_nested_fields(df)

    df["content"] = df["content"].astype(str).map(clean_text)
    df = df[df["content"].str.len() > 0].copy()

    # date a datetime si es posible
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = df.drop_duplicates(subset=["content", "date", "user"])

    keep_cols = [
    "source_type", "platform", "date", "user", "content",
    "likes", "shares", "comments", "source_url"
    ]
    return df[keep_cols]


def main():
    p = argparse.ArgumentParser(description="Unifica CSVs crudos de redes sociales (Apify/X/TikTok/Facebook) a social_clean.csv")
    p.add_argument("--raw-dir", default="data/raw", help="Carpeta con CSVs crudos")
    p.add_argument("--out", default="data/processed/social_clean.csv", help="Salida unificada")
    args = p.parse_args()

    raw_dir = Path(args.raw_dir)
    if not raw_dir.exists():
        raise FileNotFoundError(f"No existe raw-dir: {raw_dir}")

    all_frames = []

    # Ajusta patrones a tu naming real
    patterns = [
        ("x_campaign_*.csv", "x"),
        ("dataset_tweet-scraper_*.csv", "x"),
        ("tweet-scraper_*.csv", "x"),
        ("twitter_*.csv", "x"),
        ("dataset_facebook-posts-scraper_*.csv", "facebook"),
        ("dataset_facebook-search-scraper_*.csv", "facebook"),
        ("facebook_*.csv", "facebook"),
        ("dataset_tiktok-scraper_*.csv", "tiktok"),
        ("tiktok_*.csv", "tiktok"),
        ("apify_*.csv", "apify"),
    ]

    for glob_pat, default_platform in patterns:
        for path in raw_dir.glob(glob_pat):
            df = pd.read_csv(path, encoding="utf-8-sig")
            name = path.name.lower()
            platform = default_platform
            if "facebook" in name:
                platform = "facebook"
            elif "tiktok" in name:
                platform = "tiktok"
            elif "x_" in name or "twitter" in name:
                platform = "x"
            all_frames.append(normalize_df(df, platform))

    if not all_frames:
        raise FileNotFoundError(f"No se encontraron CSVs en {raw_dir} con los patrones esperados.")

    merged = pd.concat(all_frames, ignore_index=True)
    merged = merged.drop_duplicates(subset=["content", "date", "user"])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[DONE] Limpieza completa: {out_path} | Filas: {len(merged)}")


if __name__ == "__main__":
    main()
