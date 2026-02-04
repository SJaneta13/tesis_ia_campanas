from pathlib import Path
import pandas as pd
from transformers import pipeline
from tqdm import tqdm


INPUT_PATH = Path("data/processed/social_clean.csv")
OUT_PATH = Path("data/processed/social_sentiment.csv")

MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
BATCH_SIZE = 16


def main():
	if not INPUT_PATH.exists():
		raise FileNotFoundError("Falta data/processed/social_clean.csv. Ejecuta clean_scraped_data.py")

	df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
	texts = df["content"].fillna("").astype(str).tolist()

	sentiment = pipeline(
		"sentiment-analysis",
		model=MODEL_NAME,
		tokenizer=MODEL_NAME,
		truncation=True,
		max_length=512,
		padding=True,
		top_k=None,
	)

	results = []
	for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Analizando sentimiento"):
		batch = texts[i:i + BATCH_SIZE]
		preds_batch = sentiment(batch, truncation=True, max_length=512)
		for preds in preds_batch:
			if isinstance(preds, list) and preds:
				best = max(preds, key=lambda x: x.get("score", 0))
			else:
				best = {"label": "UNKNOWN", "score": 0.0}
			results.append(best)

	df["sentiment_label"] = [r["label"] for r in results]
	df["sentiment_score"] = [r["score"] for r in results]

	OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
	df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
	print(f"Sentimiento guardado en: {OUT_PATH}")


if __name__ == "__main__":
	main()
