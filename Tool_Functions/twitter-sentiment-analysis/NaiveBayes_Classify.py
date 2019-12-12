from __future__ import division
import json
import pandas as pd
import numpy as np
import requests
import nltk
import string
import re
import os
from os import path
from time import sleep
from collections import Counter
from nltk.tokenize import TweetTokenizer
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import twitter_samples
from random import shuffle

# abstraction:
# https://www.nltk.org/api/nltk.tokenize.html
# https://kite.com/python/docs/nltk.TweetTokenizer
# https://blog.chapagain.com.np/python-nltk-twitter-sentiment-analysis-natural-language-processing-nlp/
# https://www.kaggle.com/nicewinter/gop-twitter-sentiment-analysis-in-python
# https://stackoverflow.com/questions/20827741/nltk-naivebayesclassifier-training-for-sentiment-analysis

def cleanTweet(tweet):
    # make lowercase
    tweet = tweet.lower()
    # remove all newlines from inside strings
    tweet = tweet.replace('\n', "").strip()
    # remove unicode left/right quote characters
    tweet = tweet.replace(u'\u2018', '\'').replace(u'\u2019', '\'')
    # convert abbreviations
    # i.e. couldn't -> could not
    tweet = tweet.replace("n\'t", " not")
    # remove any non-ascii characters
    tweet = re.sub(r"[^\x00-\x7F]+", "", tweet)
    # remove stock market tickers
    tweet = re.sub(r"\$\w*", "", tweet)
    # remove old-school retweet text RT
    tweet = re.sub(r"^RT[\s]+", "", tweet)
    # remove hyperlinks
    tweet = re.sub(r"https?:\/\/.*[\r\n]*", "", tweet)
    # remove hashtags
    tweet = re.sub(r"#", "", tweet)
    return tweet

def tokenizeTweets(tweetList):
    useless_ones = nltk.corpus.stopwords.words("english") + list(string.punctuation)
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=False, reduce_len=False)
    retTweetList = []
    for tweet in tweetList:
        wordlist = [word for word in tokenizer.tokenize(tweet) if word not in useless_ones]
        retTweetList.append(wordlist)
    return retTweetList

def stemTweets(tweetList):
    sno = nltk.stem.SnowballStemmer("english")
    retTweetList = []
    for words in tweetList:
        stemmed_words = [sno.stem(word) for word in words]
        retTweetList.append(stemmed_words)
    return retTweetList

# simplest model for analyzing text is to think of it as an unordered list of words
# known as bag-of-words model
# this allows us to infer the category, topic, or sentiment
# from bag-of-words model we can build features to be used by classifier
# in this method we assume that each word is a feature that can either be True or False
# this is implemented in Python as a dictionary where for each word in a sentence we associate True,
# if a word is missing, that would be the same as assigning False
def buildBowFeatures(words):
    return {word:True for word in words}

#fp = "C:/Users/Matt/Documents/GitHub/twitter-sentiment-analysis/"
def main(twtInfo: object):
    data_tcs_tweets = pd.read_json(twtInfo, orient="records")
    tweets = data_tcs_tweets["text"]
    data_id = data_tcs_tweets["id"]
    nltk.download("twitter_samples")
    pos_tweets = twitter_samples.strings("positive_tweets.json")
    neg_tweets = twitter_samples.strings("negative_tweets.json")
    clean_pos_tweets = [cleanTweet(tweet) for tweet in pos_tweets]
    clean_neg_tweets = [cleanTweet(tweet) for tweet in neg_tweets]
    # downloads corpus of stopwords (i.e. "the", "did", "?")
    # TODO: check if nltk.stopwords is already downloaded and if it is, then skip
    nltk.download("stopwords")
    # downloads work tokenizer trained on English
    # TODO: check if nltk.punkt is already downloaded and if it is, then skip
    nltk.download("punkt")
    # tokenize and clean up the whole set of clean tweet texts
    # tc_tweets = tokenized & cleaned tweets
    pos_tc_tweets = tokenizeTweets(clean_pos_tweets)
    neg_tc_tweets = tokenizeTweets(clean_neg_tweets)
    # apply stemming algorithm to tweets
    # stemming normalizes text i.e. "waited", "waits", "waiting" -> "wait"
    # this cleans the data and makes it easier for the ML algorithm to read it
    pos_tcs_tweets = stemTweets(pos_tc_tweets)
    neg_tcs_tweets = stemTweets(neg_tc_tweets)
    # pairs each tweet's cleaned text with its sentiment label
    pos_label_pair_list = ((tweet, "pos") for tweet in pos_tcs_tweets)
    neg_label_pair_list = ((tweet, "neg") for tweet in neg_tcs_tweets)
    # TODO: possible bias location, we are only separating into positive/negative sentiment and not neutral
    # remove all neutral tweets since we are only interested in positive/negative ones
    #text_label_pair_list[:] = [tuple for tuple in text_label_pair_list if tuple[1] != "Neutral"]
    # split into train and test set, 90% for training set, 10% for testing set
    #train, test = train_test_split(text_label_pair_list, test_size = 0.1, random_state=7)
    # define bag-of-words model and features
    pos_bow = [(buildBowFeatures(tuple[0]), tuple[1]) for tuple in pos_label_pair_list]
    neg_bow = [(buildBowFeatures(tuple[0]), tuple[1]) for tuple in neg_label_pair_list]
    data_bow = [buildBowFeatures(text) for text in tweets]
    # one of the simplest supervised ML classifiers is the Naive Bayes Classifier
    # TODO: potential new tool would involve different ML classifier
    # it can be trained on 90% of the data to learn what words are associated with pos/neg comments
    train_bow = pos_bow + neg_bow
    shuffle(train_bow)
    sentiment_classifier = NaiveBayesClassifier.train(train_bow)
    # we can check after training what the accuracy is on the training set
    # i.e. the same data we used for training, this should be a high number since algo already saw the data
    #nltk.classify.util.accuracy(sentiment_classifier, train_bow)*100
    # accuracy on the testing set
    #nltk.classify.util.accuracy(sentiment_classifier, test_bow)*100
    preds = [sentiment_classifier.classify(comment_dict) for comment_dict in data_bow]
    # TODO: figure out what to return
    #return pd.Series(rxt_params).to_json(orient="records")
    #dfPreds = pd.DataFrame(preds)
    #ret = pd.concat([data, dfPreds], axis=1)
    ret = []
    for i in range(len(preds)):
        ret.append({})
        ret[i]["text"] = tweets[i]
        ret[i]["id"] = data_id[i]
        ret[i]["sentiment"] = preds[i]
    return pd.Series(ret).to_json(orient="records")
    
dat = main("C:/Users/Matt/Documents/GitHub/twitter-sentiment-analysis/test_token_out.json")
with open("test_out.json", "w+") as out:
    out.write(dat)