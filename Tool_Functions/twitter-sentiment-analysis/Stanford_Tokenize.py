import json
import pandas as pd
import string
import nltk
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize
import os

# stop words to remove from text
nltk.download("stopwords")
# also removing @ in this case since Stanford Tokenizer tokenizes them
useless_ones = nltk.corpus.stopwords.words("english") + list(string.punctuation) + ['@']
# workaround for adding environment variable for tagger
jar = 'stanford-postagger.jar'
model = 'english-bidirectional-distsim.tagger'
pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')
# set java path in environment
java_path = 'C:/Program Files/Java/jdk-13/bin/java.exe'
os.environ['JAVAHOME'] = java_path

def tokenizeTweets(tweetList):
    retTweetList = []
    for tweet in tweetList:
        wordlist = [word for word in pos_tagger.tag(word_tokenize(tweet)) if word not in useless_ones]
        retTweetList.append(wordlist)
    return retTweetList

def tokenizeTweet(tweet):
    wordlist = [word[0] for word in pos_tagger.tag(word_tokenize(tweet)) if word not in useless_ones]
    return wordlist

def main(twtInfo:object):
    clean_data_tweets = pd.read_json(twtInfo, orient="records")
    tweets = clean_data_tweets["text"]
    data_id = clean_data_tweets["id"]
    data_tc_tweets = []
    for tweet in tweets:
        data_tc_tweets.append(tokenizeTweet(tweet))
    ret = []
    for i in range(len(data_tc_tweets)):
        ret.append({})
        ret[i]["text"] = data_tc_tweets[i]
        ret[i]["id"] = data_id[i]
    return pd.Series(ret).to_json(orient="records")
