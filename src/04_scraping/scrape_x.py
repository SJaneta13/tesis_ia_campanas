import os
from datetime import datetime
import snscrape.modules.twitter as sntwitter
import pandas as pd


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
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"data/raw/x_campaign_{ts}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"Guardado: {out_path} | Filas: {len(df)}")


if __name__ == "__main__":
    main()
