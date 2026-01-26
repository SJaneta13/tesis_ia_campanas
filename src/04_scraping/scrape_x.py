import snscrape.modules.twitter as sntwitter
import pandas as pd

query = "Noboa OR 'Luisa González' since:2025-01-01 until:2025-04-30"
tweets = []

for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
    if i > 3000:
        break
    tweets.append({
        "date": tweet.date,
        "user": tweet.user.username,
        "content": tweet.content,
        "likes": tweet.likeCount,
        "retweets": tweet.retweetCount
    })

df = pd.DataFrame(tweets)
df.to_csv("data/raw/x_campaign_2025.csv", index=False)
