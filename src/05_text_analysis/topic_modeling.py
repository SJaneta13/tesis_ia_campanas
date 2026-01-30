from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF


INPUT_PATH = Path("data/processed/social_clean.csv")
OUT_DIR = Path("outputs/latest/tables")
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_TOPICS = 6
TOP_WORDS = 10


def main():
	if not INPUT_PATH.exists():
		raise FileNotFoundError("Falta data/processed/social_clean.csv. Ejecuta clean_scraped_data.py")

	df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
	texts = df["content"].fillna("").astype(str)

	vectorizer = TfidfVectorizer(
		max_df=0.95,
		min_df=2,
		ngram_range=(1, 2),
		max_features=8000,
	)
	X = vectorizer.fit_transform(texts)

	nmf = NMF(n_components=N_TOPICS, random_state=42)
	W = nmf.fit_transform(X)
	H = nmf.components_

	terms = vectorizer.get_feature_names_out()
	topics = []
	for i, comp in enumerate(H):
		top_idx = comp.argsort()[-TOP_WORDS:][::-1]
		words = [terms[j] for j in top_idx]
		topics.append({"topic": i, "top_words": ", ".join(words)})

	topics_df = pd.DataFrame(topics)
	topics_path = OUT_DIR / "social_topics.csv"
	topics_df.to_csv(topics_path, index=False, encoding="utf-8-sig")

	df["topic"] = W.argmax(axis=1)
	assigned_path = Path("data/processed/social_topics_assigned.csv")
	assigned_path.parent.mkdir(parents=True, exist_ok=True)
	df.to_csv(assigned_path, index=False, encoding="utf-8-sig")

	print(f"Tópicos guardados en: {topics_path}")
	print(f"Asignaciones guardadas en: {assigned_path}")


if __name__ == "__main__":
	main()
