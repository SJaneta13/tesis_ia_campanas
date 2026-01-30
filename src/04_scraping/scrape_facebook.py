import os
import requests
import pandas as pd
from datetime import datetime


# =====================================
# CONFIG (Facebook Graph API)
# =====================================
# Requiere:
# - FACEBOOK_PAGE_ID
# - FACEBOOK_ACCESS_TOKEN
# Opcionales:
# - FACEBOOK_SINCE (YYYY-MM-DD)
# - FACEBOOK_UNTIL (YYYY-MM-DD)
# - FACEBOOK_LIMIT (int)

PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
SINCE = os.getenv("FACEBOOK_SINCE", "2025-01-01")
UNTIL = os.getenv("FACEBOOK_UNTIL", "2025-04-30")
LIMIT = int(os.getenv("FACEBOOK_LIMIT", "100"))

if not PAGE_ID or not ACCESS_TOKEN:
	raise RuntimeError(
		"Faltan credenciales. Define FACEBOOK_PAGE_ID y FACEBOOK_ACCESS_TOKEN en el entorno."
	)

BASE_URL = f"https://graph.facebook.com/v19.0/{PAGE_ID}/posts"
FIELDS = "created_time,message,permalink_url,shares,likes.summary(true),comments.summary(true)"


def fetch_facebook_posts():
	params = {
		"access_token": ACCESS_TOKEN,
		"fields": FIELDS,
		"since": SINCE,
		"until": UNTIL,
		"limit": LIMIT,
	}

	all_rows = []
	next_url = BASE_URL

	while next_url:
		resp = requests.get(next_url, params=params, timeout=30)
		resp.raise_for_status()
		data = resp.json()

		for item in data.get("data", []):
			all_rows.append(
				{
					"platform": "facebook",
					"date": item.get("created_time"),
					"user": PAGE_ID,
					"content": item.get("message", ""),
					"likes": item.get("likes", {}).get("summary", {}).get("total_count", 0),
					"shares": item.get("shares", {}).get("count", 0),
					"comments": item.get("comments", {}).get("summary", {}).get("total_count", 0),
					"source_url": item.get("permalink_url", ""),
					"post_id": item.get("id"),
				}
			)

		paging = data.get("paging", {})
		next_url = paging.get("next")
		params = None

	return all_rows


def main():
	rows = fetch_facebook_posts()
	df = pd.DataFrame(rows)

	ts = datetime.now().strftime("%Y%m%d_%H%M%S")
	out_path = f"data/raw/facebook_{PAGE_ID}_{ts}.csv"
	df.to_csv(out_path, index=False, encoding="utf-8-sig")
	print(f"Guardado: {out_path} | Filas: {len(df)}")


if __name__ == "__main__":
	main()
