from nltk.stem.snowball import SnowballStemmer
import pandas as pd

def stemTweets(tweetList):
    sno = SnowballStemmer("english")
    retTweetList = []
    for words in tweetList:
        stemmed_words = [sno.stem(word) for word in words]
        retTweetList.append(stemmed_words)
    return retTweetList

def stemTweet(tweet):
    sno = SnowballStemmer("english")
    stemmed_words = [sno.stem(word) for word in tweet]
    return stemmed_words

def main(twtInfo:object):
    data_tc_tweets = pd.read_json(twtInfo, orient="records")
    tweets = data_tc_tweets['text']
    data_id = data_tc_tweets['id']
    data_tcs_tweets = []
    for tweet in tweets:
        data_tcs_tweets.append(stemTweet(tweet))
    ret = []
    for i in range(len(data_tcs_tweets)):
        ret.append({})
        ret[i]['text'] = data_tcs_tweets[i]
        ret[i]['id'] = data_id[i]
    return pd.Series(ret).to_json(orient='records')

