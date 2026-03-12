from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pandas as pd
from transformers import pipeline
from tqdm import tqdm


DEFAULT_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"


def summarize(subdf: pd.DataFrame, group: str) -> pd.DataFrame:
    vc = subdf["sentiment_label"].value_counts()
    if vc.sum() == 0:
        return pd.DataFrame(columns=["group", "sentiment_label", "count", "pct"])

    out = (vc / vc.sum() * 100).round(1).reset_index()
    out.columns = ["sentiment_label", "pct"]
    out["count"] = vc.values
    out["group"] = group
    return out[["group", "sentiment_label", "count", "pct"]]


def map_label_to_es(x: str) -> str:
    x = str(x).lower()
    if "neg" in x:
        return "negativo"
    if "neu" in x:
        return "neutral"
    if "pos" in x:
        return "positivo"
    return "neutral"


def infer_text_col(df: pd.DataFrame, text_col: Optional[str]) -> str:
    if text_col and text_col in df.columns:
        return text_col
    if "text" in df.columns:
        return "text"      # news pipeline
    if "content" in df.columns:
        return "content"   # social pipeline
    raise KeyError("No encuentro columna de texto. Esperaba 'text' (news) o 'content' (social).")


def _pick_best_pred(pred):
    """
    Algunos pipelines pueden devolver:
    - dict: {"label": "...", "score": ...}
    - list[dict]: [{"label": "...", "score": ...}, ...]
    Aquí normalizamos a un dict.
    """
    if isinstance(pred, list) and pred:
        return max(pred, key=lambda x: float(x.get("score", 0.0)))
    if isinstance(pred, dict):
        return pred
    return {"label": "UNKNOWN", "score": 0.0}


def main():
    p = argparse.ArgumentParser(description="Sentiment analysis (NEWS/SOCIAL) usando modelo multilingüe.")
    p.add_argument("--input", required=True, help="CSV de entrada (news o social)")
    p.add_argument("--outdir", default="outputs/latest/tables", help="Carpeta donde guardar outputs")
    p.add_argument("--prefix", default="news", help="Prefijo de salida: news o social")
    p.add_argument("--model", default=DEFAULT_MODEL, help="HuggingFace model id")
    p.add_argument("--text-col", default="", help="Columna con texto. Vacío = auto (text o content)")
    p.add_argument("--lang", default="", help="English/Spanish. Vacío = no filtra por language.")
    p.add_argument("--ai-col", default="is_ai_related", help="Columna booleana IA. (si no existe, ignora)")
    p.add_argument("--max-chars", type=int, default=1500, help="Recorta texto por eficiencia")
    p.add_argument("--batch", type=int, default=16, help="Batch size inferencia")
    args = p.parse_args()

    inpath = Path(args.input)
    if not inpath.exists():
        raise FileNotFoundError(f"No existe input: {inpath}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(inpath, encoding="utf-8-sig")
    text_col = infer_text_col(df, args.text_col.strip() or None)

    # limpiar texto
    df[text_col] = df[text_col].fillna("").astype(str).str.strip()
    df = df[df[text_col] != ""].copy()

    # filtro opcional por idioma (solo si tiene columna)
    if args.lang.strip():
        if "language" not in df.columns:
            print("[WARN] --lang fue provisto pero el CSV no tiene columna 'language'. Se ignora filtro.")
        else:
            df["language"] = df["language"].fillna("").astype(str).str.strip()
            df = df[df["language"].str.lower() == args.lang.lower()].copy()

    # recorte para modelo
    if args.max_chars and args.max_chars > 0:
        df["text_model"] = df[text_col].str.slice(0, args.max_chars)
    else:
        df["text_model"] = df[text_col]

    clf = pipeline(
        "sentiment-analysis",
        model=args.model,
        tokenizer=args.model,
        truncation=True,
        max_length=512,
        padding=True,
        top_k=None,  # permite compatibilidad si devuelve lista de labels
    )

    labels_raw = []
    scores_raw = []
    texts = df["text_model"].tolist()

    for i in tqdm(range(0, len(texts), args.batch), desc=f"Sentiment ({args.prefix})"):
        batch = texts[i : i + args.batch]
        preds = clf(batch)
        for pred in preds:
            best = _pick_best_pred(pred)
            labels_raw.append(best.get("label", "UNKNOWN"))
            scores_raw.append(float(best.get("score", 0.0)))

    df["sentiment_raw_label"] = labels_raw
    df["sentiment_raw_score"] = scores_raw
    df["sentiment_label"] = df["sentiment_raw_label"].apply(map_label_to_es)
    df["sentiment_score"] = df["sentiment_raw_score"]

    # resumen all + ai_only si aplica
    summary_parts = [summarize(df, "all")]

    ai_col = args.ai_col.strip()
    if ai_col and ai_col in df.columns:
        df_ai = df[df[ai_col] == True].copy()
        summary_parts.append(summarize(df_ai, "ai_only"))
    else:
        df_ai = pd.DataFrame()

    summary = pd.concat(summary_parts, ignore_index=True)

    scored_path = outdir / f"{args.prefix}_sentiment_scored.csv"
    summary_path = outdir / f"{args.prefix}_sentiment_summary.csv"

    df.to_csv(scored_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print(f"[DONE] saved: {scored_path}")
    print(f"[DONE] saved: {summary_path}")
    print(f"N ({args.prefix}): {len(df)}")
    if len(df_ai):
        print(f"N ai_only ({args.prefix}): {len(df_ai)}")


if __name__ == "__main__":
    main()
