import os
import requests
import pandas as pd
from datetime import datetime


# =====================================
# CONFIG (TikTok API)
# =====================================
# Esta implementación es genérica y requiere:
# - TIKTOK_API_BASE_URL (ej: https://open.tiktokapis.com/v2)
# - TIKTOK_API_ENDPOINT (ej: /research/video/query/)
# - TIKTOK_API_KEY (Bearer token o key del proveedor)
# Opcionales:
# - TIKTOK_API_HOST (si usas RapidAPI)
# - TIKTOK_QUERY (texto)
# - TIKTOK_START_DATE / TIKTOK_END_DATE (YYYY-MM-DD)
# - TIKTOK_LIMIT (int)

BASE_URL = os.getenv("TIKTOK_API_BASE_URL")
ENDPOINT = os.getenv("TIKTOK_API_ENDPOINT")
API_KEY = os.getenv("TIKTOK_API_KEY")
API_HOST = os.getenv("TIKTOK_API_HOST")

QUERY = os.getenv("TIKTOK_QUERY", "Noboa OR \"Luisa González\"")
START_DATE = os.getenv("TIKTOK_START_DATE", "2025-01-01")
END_DATE = os.getenv("TIKTOK_END_DATE", "2025-04-30")
LIMIT = int(os.getenv("TIKTOK_LIMIT", "100"))

if not BASE_URL or not ENDPOINT or not API_KEY:
	raise RuntimeError(
		"Config incompleta. Define TIKTOK_API_BASE_URL, TIKTOK_API_ENDPOINT y TIKTOK_API_KEY."
	)


def fetch_tiktok_posts():
	url = f"{BASE_URL.rstrip('/')}{ENDPOINT}"

	headers = {
		"Authorization": f"Bearer {API_KEY}",
		"Content-Type": "application/json",
	}
	if API_HOST:
		headers["X-RapidAPI-Host"] = API_HOST
		headers["X-RapidAPI-Key"] = API_KEY

	payload = {
		"query": QUERY,
		"start_date": START_DATE,
		"end_date": END_DATE,
		"max_count": LIMIT,
	}

	resp = requests.post(url, headers=headers, json=payload, timeout=60)
	resp.raise_for_status()
	data = resp.json()

	rows = []
	for item in data.get("data", []):
		rows.append(
			{
				"platform": "tiktok",
				"date": item.get("create_time") or item.get("createTime"),
				"user": item.get("author", {}).get("unique_id")
				or item.get("author", {}).get("uniqueId"),
				"content": item.get("desc") or item.get("text") or "",
				"likes": item.get("stats", {}).get("digg_count", 0)
				or item.get("stats", {}).get("diggCount", 0),
				"shares": item.get("stats", {}).get("share_count", 0)
				or item.get("stats", {}).get("shareCount", 0),
				"comments": item.get("stats", {}).get("comment_count", 0)
				or item.get("stats", {}).get("commentCount", 0),
				"source_url": item.get("share_url") or item.get("shareUrl") or "",
				"post_id": item.get("id") or item.get("video_id"),
			}
		)

	return rows


def main():
	rows = fetch_tiktok_posts()
	df = pd.DataFrame(rows)

	ts = datetime.now().strftime("%Y%m%d_%H%M%S")
	out_path = f"data/raw/tiktok_{ts}.csv"
	df.to_csv(out_path, index=False, encoding="utf-8-sig")
	print(f"Guardado: {out_path} | Filas: {len(df)}")


if __name__ == "__main__":
	main()
