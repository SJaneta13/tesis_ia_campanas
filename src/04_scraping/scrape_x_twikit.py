from __future__ import annotations

import argparse
import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

from twikit import Client


def build_queries() -> list[str]:
    since = "2025-02-01"
    until = "2025-05-01"
    base = f"since:{since} until:{until} lang:es -filter:retweets"
    return [
        f'("Daniel Noboa" OR Noboa) {base}',
        f'("Luisa González" OR "Luisa Gonzalez") {base}',
        f'(deepfake OR bots OR bot OR "inteligencia artificial" OR IA) (Noboa OR "Luisa González" OR "Luisa Gonzalez") {base}',
    ]


async def login_client(cookies_file: Path) -> Client:
    client = Client("es-EC")

    if cookies_file.exists():
        client.load_cookies(str(cookies_file))
        return client

    username = os.getenv("X_USER")
    email = os.getenv("X_EMAIL")
    password = os.getenv("X_PASS")

    if not password or (not username and not email):
        raise RuntimeError("Define X_PASS y al menos X_USER o X_EMAIL en variables de entorno.")

    # Login robusto: prueba username primero, luego email
    try:
        if username:
            await client.login(auth_info_1=username, password=password)
        else:
            raise Exception("no username")
    except Exception:
        await client.login(auth_info_1=email, password=password)

    client.save_cookies(str(cookies_file))
    return client


async def search_query(client: Client, query: str, max_tweets: int) -> list[dict]:
    rows = []
    tweets = await client.search_tweet(query, product="Latest")

    while tweets and len(rows) < max_tweets:
        for t in tweets:
            if len(rows) >= max_tweets:
                break

            user = getattr(t, "user", None)
            username = getattr(user, "screen_name", None)

            rows.append({
                "tweet_id": getattr(t, "id", None),
                "url": f"https://x.com/{username}/status/{getattr(t, 'id', '')}" if username else None,
                "created_at": getattr(t, "created_at_datetime", None) or getattr(t, "created_at", None),
                "username": username,
                "displayname": getattr(user, "name", None),
                "content": getattr(t, "text", None),
                "lang": getattr(t, "lang", None),
                "likeCount": getattr(t, "favorite_count", None),
                "retweetCount": getattr(t, "retweet_count", None),
                "replyCount": getattr(t, "reply_count", None),
                "quoteCount": getattr(t, "quote_count", None),
                "query": query,
            })

        try:
            tweets = await tweets.next()
        except Exception:
            break

    return rows


async def main_async(max_tweets: int, outdir: Path, cookies_file: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    client = await login_client(cookies_file)

    all_rows = []
    for q in build_queries():
        rows = await search_query(client, q, max_tweets=max_tweets)
        all_rows.extend(rows)
        print(f"[OK] {len(rows)} tweets for query: {q[:60]}...")

    df = pd.DataFrame(all_rows)
    if "tweet_id" in df.columns:
        df = df.drop_duplicates(subset=["tweet_id"])

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    outfile = outdir / f"x_scrape_feb_apr_2025_{run_id}.csv"
    df.to_csv(outfile, index=False, encoding="utf-8")

    meta = {
        "run_id": run_id,
        "n_rows": int(len(df)),
        "n_queries": 3,
        "max_tweets_per_query": max_tweets,
        "out_file": str(outfile),
        "cookies_file": str(cookies_file),
        "method": "twikit_login_no_api_key",
    }
    (outdir / f"run_{run_id}_meta.json").write_text(pd.Series(meta).to_json(), encoding="utf-8")
    print(f"[DONE] saved: {outfile} ({len(df)} rows)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max-tweets", type=int, default=50)
    p.add_argument("--outdir", type=str, default="data/external/x")
    p.add_argument("--cookies", type=str, default="cookies_x.json")
    args = p.parse_args()

    asyncio.run(main_async(args.max_tweets, Path(args.outdir), Path(args.cookies)))


if __name__ == "__main__":
    main()
