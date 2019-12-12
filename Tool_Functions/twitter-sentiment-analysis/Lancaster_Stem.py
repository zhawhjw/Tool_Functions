import pandas as pd
from nltk.stem.lancaster import LancasterStemmer

# maximum -> maxim
# presumably -> presum
# multiply -> multiply
# provision -> provid
# owed -> ow
# ear -> ear
# saying -> say
# crying -> cry
# string -> string
# meant -> meant
# cement -> cem

def stemTweets(tweetList):
    lan = LancasterStemmer()
    retTweetList = []
    for words in tweetList:
        stemmed_words = [lan.stem(word) for word in words]
        retTweetList.append(stemmed_words)
    return retTweetList

def stemTweet(tweet):
    lan = LancasterStemmer()
    stemmed_words = [lan.stem(word) for word in tweet]
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

