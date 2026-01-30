import os
import json
import argparse
from datetime import datetime
from pathlib import Path
import requests
import pandas as pd


# =====================================
# Scraper genérico usando Apify Actors
# =====================================
# Requiere:
# - APIFY_TOKEN
# Parámetros:
# - --actor apify/facebook-posts-scraper
# - --input src/04_scraping/apify_inputs/facebook_posts.json

API_BASE = "https://api.apify.com/v2"
RAW_DIR = Path("data/raw")


def run_actor(actor: str, input_payload: dict, token: str, wait_seconds: int = 120):
	actor_id = actor.replace("/", "~")
	url = f"{API_BASE}/acts/{actor_id}/runs"
	params = {"token": token, "waitForFinish": wait_seconds}
	resp = requests.post(url, params=params, json=input_payload, timeout=60)
	resp.raise_for_status()
	data = resp.json().get("data", {})
	return data


def fetch_dataset_items(dataset_id: str, token: str):
	url = f"{API_BASE}/datasets/{dataset_id}/items"
	params = {
		"token": token,
		"format": "json",
		"clean": "true",
	}
	resp = requests.get(url, params=params, timeout=60)
	resp.raise_for_status()
	return resp.json()


def main():
	parser = argparse.ArgumentParser(description="Ejecuta un Actor de Apify y guarda CSV en data/raw.")
	parser.add_argument("--actor", default=os.getenv("APIFY_ACTOR"), help="Nombre del Actor (ej: apify/facebook-posts-scraper)")
	parser.add_argument("--input", default=os.getenv("APIFY_INPUT_PATH"), help="Ruta al JSON de input")
	parser.add_argument("--wait", type=int, default=int(os.getenv("APIFY_WAIT", "120")), help="Segundos de espera")
	args = parser.parse_args()

	token = os.getenv("APIFY_TOKEN")
	if not token:
		raise RuntimeError("Falta APIFY_TOKEN en el entorno.")
	if not args.actor:
		raise RuntimeError("Falta --actor o APIFY_ACTOR.")
	if not args.input:
		raise RuntimeError("Falta --input o APIFY_INPUT_PATH.")

	with open(args.input, "r", encoding="utf-8") as f:
		input_payload = json.load(f)

	run_data = run_actor(args.actor, input_payload, token, wait_seconds=args.wait)
	dataset_id = run_data.get("defaultDatasetId")
	if not dataset_id:
		raise RuntimeError(f"No se obtuvo datasetId. Estado: {run_data.get('status')}")

	items = fetch_dataset_items(dataset_id, token)
	if not isinstance(items, list):
		items = [items]

	raw_dir = RAW_DIR
	raw_dir.mkdir(parents=True, exist_ok=True)
	ts = datetime.now().strftime("%Y%m%d_%H%M%S")
	actor_slug = args.actor.replace("/", "_")
	out_path = raw_dir / f"apify_{actor_slug}_{ts}.csv"

	pd.DataFrame(items).to_csv(out_path, index=False, encoding="utf-8-sig")
	print(f"Guardado: {out_path} | Filas: {len(items)} | Dataset: {dataset_id}")


if __name__ == "__main__":
	main()
