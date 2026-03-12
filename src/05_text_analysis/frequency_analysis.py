# src/05_text_analysis/frequency_analysis.py
import argparse
from pathlib import Path
from collections import Counter
import re

import pandas as pd
import nltk
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


# Stopwords manuales (complemento). No reemplaza NLTK; se une a NLTK.
SPANISH_STOPWORDS_EXTRA = {
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por",
    "un", "para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero",
    "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando",
    "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien",
    "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra",
    "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos",
    "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos",
    "mucho", "quienes", "nada", "muchos", "cual", "poco", "ella", "estar",
    "estas", "algunas", "algo", "nosotros", "mi", "mis", "tú", "te", "ti",
}


def get_stopwords(lang: str, include_extra: bool = True) -> set[str]:
    lang = (lang or "").lower()

    if lang == "english":
        return set(ENGLISH_STOP_WORDS)

    if lang == "spanish":
        nltk.download("stopwords", quiet=True)
        from nltk.corpus import stopwords
        base = set(stopwords.words("spanish"))
        if include_extra:
            base |= SPANISH_STOPWORDS_EXTRA
        return base

    return set()


def tokenize(text: str, stopwords: set[str]) -> list[str]:
    text = str(text or "").lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    # Permite español (áéíóúüñ) y letras unicode
    text = re.sub(r"[^a-záéíóúüñ\s]", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()

    toks = text.split()
    return [t for t in toks if t not in stopwords and len(t) > 2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="CSV de entrada")
    p.add_argument("--text-col", default="text", help="Columna de texto: text (news) o content (social)")
    p.add_argument("--lang", default="Spanish", help="English o Spanish (stopwords)")
    p.add_argument("--top", type=int, default=30)
    p.add_argument("--outdir", default="outputs/text_analysis")
    p.add_argument("--outfile", default="frequency_top_terms.csv")
    p.add_argument("--no-extra-stopwords", action="store_true",
                   help="Si se usa, NO añade la lista manual SPANISH_STOPWORDS_EXTRA.")
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input, encoding="utf-8-sig")
    if args.text_col not in df.columns:
        raise ValueError(
            f"Falta columna '{args.text_col}' en {args.input}. Columnas: {list(df.columns)}"
        )

    stop = get_stopwords(args.lang, include_extra=not args.no_extra_stopwords)

    tokens: list[str] = []
    for t in df[args.text_col].fillna("").astype(str):
        tokens.extend(tokenize(t, stop))

    freq = Counter(tokens).most_common(args.top)
    out_df = pd.DataFrame(freq, columns=["word", "frequency"])

    outfile = outdir / args.outfile
    out_df.to_csv(outfile, index=False, encoding="utf-8-sig")
    print(f"[DONE] Frequency analysis saved to {outfile}")


if __name__ == "__main__":
    main()
