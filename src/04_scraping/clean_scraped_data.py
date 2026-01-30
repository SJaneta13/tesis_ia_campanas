import re
import json
import ast
from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
OUT_PATH = Path("data/processed/social_clean.csv")


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


def normalize_df(df: pd.DataFrame, platform: str) -> pd.DataFrame:
	col_map = {
		"date": "date",
		"created_time": "date",
		"timestamp": "date",
		"createTime": "date",
		"createdAt": "date",
		"user": "user",
		"username": "user",
		"authorUsername": "user",
		"authorName": "user",
		"unique_id": "user",
		"uniqueId": "user",
		"pageName": "user",
		"pageId": "user",
		"content": "content",
		"message": "content",
		"text": "content",
		"caption": "content",
		"desc": "content",
		"likes": "likes",
		"likesCount": "likes",
		"reactionsCount": "likes",
		"diggCount": "likes",
		"shares": "shares",
		"retweets": "shares",
		"sharesCount": "shares",
		"shareCount": "shares",
		"commentsCount": "comments",
		"commentCount": "comments",
		"source_url": "source_url",
		"permalink_url": "source_url",
		"url": "source_url",
		"postUrl": "source_url",
	}

	df = df.rename(columns=col_map)
	df = df.loc[:, ~df.columns.duplicated()]
	df["platform"] = platform

	df = _fill_numeric_cols(df)
	df = _update_stats_from_dict(df)
	df = _ensure_required_cols(df)

	df["content"] = df["content"].map(clean_text)
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
	all_frames = []

	for path in RAW_DIR.glob("x_campaign_*.csv"):
		df = pd.read_csv(path, encoding="utf-8-sig")
		all_frames.append(normalize_df(df, "x"))

	for path in RAW_DIR.glob("facebook_*.csv"):
		df = pd.read_csv(path, encoding="utf-8-sig")
		all_frames.append(normalize_df(df, "facebook"))

	for path in RAW_DIR.glob("tiktok_*.csv"):
		df = pd.read_csv(path, encoding="utf-8-sig")
		all_frames.append(normalize_df(df, "tiktok"))

	for path in RAW_DIR.glob("apify_*.csv"):
		df = pd.read_csv(path, encoding="utf-8-sig")
		name = path.name.lower()
		if "facebook" in name:
			platform = "facebook"
		elif "tiktok" in name:
			platform = "tiktok"
		else:
			platform = "apify"
		all_frames.append(normalize_df(df, platform))

	if not all_frames:
		raise FileNotFoundError("No se encontraron CSVs en data/raw.")

	merged = pd.concat(all_frames, ignore_index=True)
	OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
	merged.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
	print(f"Limpieza completa: {OUT_PATH} | Filas: {len(merged)}")


if __name__ == "__main__":
	main()
