import os
from datetime import datetime
import snscrape.modules.twitter as sntwitter
import pandas as pd
from pathlib import Path


# CONFIG
# =========================
RUN_ID = os.getenv("RUN_ID") or datetime.now().strftime("%Y%m%d_%H%M")
OUTDIR = Path("data/external/social") / f"run_{RUN_ID}"
OUTDIR.mkdir(parents=True, exist_ok=True)


QUERY = os.getenv(
    "X_QUERY",
    "Noboa OR 'Luisa González' since:2025-01-01 until:2025-04-30",
)
LIMIT = int(os.getenv("X_LIMIT", "3000"))


def main():
    tweets = []

    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(QUERY).get_items()):
        if i >= LIMIT:
            break
        tweets.append(
            {
                "platform": "x",
                "date": tweet.date,
                "user": tweet.user.username,
                "content": tweet.content,
                "likes": tweet.likeCount,
                "retweets": tweet.retweetCount,
                "source_url": tweet.url,
                "post_id": tweet.id,
            }
        )

    df = pd.DataFrame(tweets)
    out_path = OUTDIR / "x_raw.csv" 
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    
    print(f"Guardado: {out_path} | Filas: {len(df)}")


if __name__ == "__main__":
    main()
