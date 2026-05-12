# src/05_text_analysis/topic_modeling.py
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import nltk
from sklearn.feature_extraction.text import (
    CountVectorizer,
    TfidfVectorizer,
    ENGLISH_STOP_WORDS,
)
from sklearn.decomposition import LatentDirichletAllocation, NMF


def get_stopwords(lang: str) -> set[str]:
    lang = (lang or "").lower()
    if lang == "english":
        return set(ENGLISH_STOP_WORDS)
    if lang == "spanish":
        nltk.download("stopwords", quiet=True)
        from nltk.corpus import stopwords
        return set(stopwords.words("spanish"))
    return set()


def get_custom_stop(lang: str) -> set[str]:
    lang = (lang or "").lower()
    if lang == "english":
        return {"ecuador", "noboa", "president", "presidential", "said", "news", "year", "country", "daniel"}
    if lang == "spanish":
        return {
            "ecuador", "noboa", "luisa", "gonzalez", "gonzález",
            "presidente", "presidencial", "dijo", "dice", "según", "segun",
            "año", "pais", "país", "elecciones", "campaña", "campana",
            "cne", "tce",
        }
    return set()


def infer_text_col(df: pd.DataFrame, text_col: Optional[str]) -> str:
    if text_col and text_col in df.columns:
        return text_col
    if "text" in df.columns:
        return "text"      # news
    if "content" in df.columns:
        return "content"   # social
    raise KeyError("No encuentro columna de texto. Esperaba 'text' (news) o 'content' (social).")


def build_vectorizer_and_matrix(
    method: str,
    series: pd.Series,
    stopwords: Optional[list[str]],
    min_df: int,
    max_df: float,
    max_features: int,
    token_pattern: str,
) -> Tuple[object, object]:
    """
    Construye el vectorizador según método y ejecuta fit_transform.
    Lanza ValueError si 'empty vocabulary' (lo manejamos arriba).
    """
    if method == "lda":
        vect = CountVectorizer(
            stop_words=stopwords,
            token_pattern=token_pattern,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features,
        )
    else:
        vect = TfidfVectorizer(
            stop_words=stopwords,
            token_pattern=token_pattern,
            max_df=max_df,
            min_df=min_df,
            ngram_range=(1, 2),
            max_features=max_features,
        )

    X = vect.fit_transform(series)
    return vect, X


def main():
    p = argparse.ArgumentParser(description="Topic modeling unificado (NEWS/SOCIAL).")
    p.add_argument("--input", required=True, help="CSV de entrada")
    p.add_argument("--outdir", default="outputs/latest/tables", help="Carpeta de salida")
    p.add_argument("--prefix", default="news", help="Prefijo de salida: news o social")
    p.add_argument("--text-col", default="", help="Columna de texto. Vacío = auto (text o content)")
    p.add_argument("--lang", default="", help="English/Spanish. Vacío = no filtra por language.")
    p.add_argument("--method", choices=["lda", "nmf"], default="lda", help="Método: lda (news) o nmf (social)")
    p.add_argument("--topics", type=int, default=6, help="Número de tópicos")
    p.add_argument("--top-words", type=int, default=10, help="Top palabras por tópico")
    p.add_argument("--max-features", type=int, default=8000, help="Max features del vectorizador")
    p.add_argument("--min-df", type=int, default=2, help="Min df")
    p.add_argument("--max-df", type=float, default=0.95, help="Max df")
    args = p.parse_args()

    inpath = Path(args.input)
    if not inpath.exists():
        raise FileNotFoundError(f"No existe input: {inpath}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(inpath, encoding="utf-8-sig")
    text_col = infer_text_col(df, args.text_col.strip() or None)

    df[text_col] = df[text_col].fillna("").astype(str).str.strip()
    df = df[df[text_col] != ""].copy()

    # filtro opcional por idioma si existe
    if args.lang.strip():
        if "language" not in df.columns:
            print("[WARN] --lang provisto pero no existe columna 'language'. Se ignora filtro.")
        else:
            df["language"] = df["language"].fillna("").astype(str).str.strip()
            df = df[df["language"].str.lower() == args.lang.lower()].copy()

    if df.empty:
        raise ValueError("Luego de limpiar/filtros el dataframe quedó vacío. Renúncia o revisa filtros (--lang, columnas).")

    # stopwords (solo si indicas lang)
    STOPWORDS: Optional[list[str]] = None
    if args.lang.strip():
        STOPWORDS = list(get_stopwords(args.lang).union(get_custom_stop(args.lang)))

    # token patterns
    token_pattern_3 = r"(?u)\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]{3,}\b"
    token_pattern_2 = r"(?u)\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]{2,}\b"

    # ---- Vectorización robusta con fallbacks ----
    try:
        vect, X = build_vectorizer_and_matrix(
            args.method, df[text_col],
            STOPWORDS, args.min_df, args.max_df, args.max_features, token_pattern_3
        )
    except ValueError as e:
        msg = str(e).lower()
        if "empty vocabulary" not in msg:
            raise

        print("[WARN] empty vocabulary con configuración actual.")
        print("       Reintentando sin stopwords y min_df=1 ...")

        try:
            vect, X = build_vectorizer_and_matrix(
                args.method, df[text_col],
                None, 1, args.max_df, args.max_features, token_pattern_3
            )
        except ValueError as e2:
            msg2 = str(e2).lower()
            if "empty vocabulary" not in msg2:
                raise

            print("[WARN] Sigue vacío. Reintentando con token_pattern de 2+ letras ...")
            vect, X = build_vectorizer_and_matrix(
                args.method, df[text_col],
                None, 1, args.max_df, args.max_features, token_pattern_2
            )

    # ---- Entrenamiento del modelo ----
    if args.method == "lda":
        model = LatentDirichletAllocation(n_components=args.topics, random_state=42)
        doc_topic = model.fit_transform(X)
        components = model.components_
    else:
        model = NMF(n_components=args.topics, random_state=42)
        W = model.fit_transform(X)
        doc_topic = W
        components = model.components_

    terms = vect.get_feature_names_out()

    # 1) términos por tópico
    rows_terms = []
    for i, comp in enumerate(components):
        top_idx = np.argsort(comp)[-args.top_words:][::-1]
        top_terms = [terms[j] for j in top_idx]
        rows_terms.append({"topic": i + 1, "top_terms": ", ".join(top_terms)})

    terms_path = outdir / f"{args.prefix}_topics_terms.csv"
    pd.DataFrame(rows_terms).to_csv(terms_path, index=False, encoding="utf-8-sig")

    # 2) documento -> tópico dominante
    df_docs = df.copy()
    df_docs["dominant_topic"] = np.argmax(doc_topic, axis=1) + 1
    df_docs["dominant_topic_score"] = np.max(doc_topic, axis=1).round(4)

    docs_path = outdir / f"{args.prefix}_topics_docs.csv"
    df_docs.to_csv(docs_path, index=False, encoding="utf-8-sig")

    print(f"[DONE] saved: {terms_path}")
    print(f"[DONE] saved: {docs_path}")
    print(f"N used ({args.prefix}): {len(df_docs)}")
    for r in rows_terms:
        print(f"Tema {r['topic']}: {r['top_terms']}")




if __name__ == "__main__":
    main()

