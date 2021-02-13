import tweepy
import pandas as pd
import os
from datetime import datetime


#Twitter Access
auth = tweepy.OAuthHandler( 'xx','xx')
auth.set_access_token('xxx','xxx')

api = tweepy.API(auth, wait_on_rate_limit = True)

msgs = []
msg =[]

for tweet in tweepy.Cursor(api.search, q='#CoronaWarnApp', rpp=100).items(3000):
    if (not tweet.retweeted) and ('RT @' not in tweet.text):
        msg = [tweet.created_at, tweet.text]
        msg = tuple(msg)
        msgs.append(msg)

today = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = "_".join([today, 'tweets.csv'])
df = pd.DataFrame(msgs, columns=[ 'date', 'text'])
df.to_csv(filename, header=True, index=False)