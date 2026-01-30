from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


INPUT_PATH = Path("data/processed/social_clean.csv")
OUT_DIR = Path("outputs/latest/tables")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SPANISH_STOPWORDS = {
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


def main():
	if not INPUT_PATH.exists():
		raise FileNotFoundError("Falta data/processed/social_clean.csv. Ejecuta clean_scraped_data.py")

	df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
	texts = df["content"].fillna("").astype(str)

	vectorizer = CountVectorizer(
		stop_words=list(SPANISH_STOPWORDS),
		ngram_range=(1, 2),
		min_df=2,
		max_features=5000,
	)
	X = vectorizer.fit_transform(texts)

	freqs = X.sum(axis=0).A1
	vocab = vectorizer.get_feature_names_out()

	out_df = pd.DataFrame({"ngram": vocab, "freq": freqs}).sort_values(
		"freq", ascending=False
	)

	out_path = OUT_DIR / "social_top_ngrams.csv"
	out_df.to_csv(out_path, index=False, encoding="utf-8-sig")
	print(f"Frecuencias guardadas en: {out_path}")


if __name__ == "__main__":
	main()
