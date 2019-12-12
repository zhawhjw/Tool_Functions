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
from PIL import Image
from bs4 import BeautifulSoup
from time import sleep
from collections import Counter
from nltk.tokenize import TweetTokenizer
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import twitter_samples
from textblob import TextBlob
from random import shuffle

# abstraction:
# https://www.nltk.org/api/nltk.tokenize.html
# https://kite.com/python/docs/nltk.TweetTokenizer
# https://blog.chapagain.com.np/python-nltk-twitter-sentiment-analysis-natural-language-processing-nlp/
# https://www.kaggle.com/nicewinter/gop-twitter-sentiment-analysis-in-python

# simplest model for analyzing text is to think of it as an unordered list of words
# known as bag-of-words model
# this allows us to infer the category, topic, or sentiment
# from bag-of-words model we can build features to be used by classifier
# in this method we assume that each word is a feature that can either be True or False
# this is implemented in Python as a dictionary where for each word in a sentence we associate True,
# if a word is missing, that would be the same as assigning False
def build_bow_features(words):
    return {word:True for word in words}

#fp = "C:/Users/Matt/Documents/GitHub/twitter-sentiment-analysis/"
def main(twtInfo: object):
    # JSON Schema:
    """
    [
        {
            "candidate": "No candidate mentioned",
            "candidate_confidence": 1,
            "candidate_gold": "",
            "id": 1,
            "name": "I_Am_Kenzi",
            "relevant_yn": "yes",
            "relevant_yn_confidence": 1,
            "relevant_yn_gold": "",
            "retweet_count": 5,
            "sentiment": "Neutral",
            "sentiment_confidence": 0.6578,
            "sentiment_gold": "",
            "subject_matter": "None of the above",
            "subject_matter_confidence": 1,
            "subject_matter_gold": "",
            "text": "RT @NancyLeeGrahn: How did everyone feel about the Climate Change question last night? Exactly. #GOPDebate",
            "tweet_coord": "",
            "tweet_created": "2015-08-07 09:54:46 -0700",
            "tweet_id": 629697200650592300,
            "tweet_location": "",
            "user_timezone": "Quito"
        },
        ...
    ]
    """
    data = pd.read_json(twtInfo, orient="records")
    pos_tweets = twitter_samples.strings("positive_tweets.json")
    neg_tweets = twitter_samples.strings("negative_tweets.json")
    # sort values by id, data in json that is in repo is already sorted by id
    data.sort_values(by="3")
    tweets = data["text"]
    labels = data["sentiment"]
    # remove all newlines from inside strings
    clean_tweets = [tweet.replace('\n', '').strip() for tweet in tweets]
    # to remove all newline characters and then all leading/trailing whitespaces from the string
    # note: strip() only removes the specified characters from the very beginning or end of a string, which is why we use replace
    # remove the unicode for the single left and right quote characters
    clean_tweets[:] = [tweet.replace(u'\u2018', '\'').replace(u'\u2019', '\'') for tweet in clean_tweets]
    # convert abbreviations
    clean_tweets[:] = [tweet.replace("n\'t", " not") for tweet in clean_tweets] # convert n't to not i.e. couldn't -> could not
    # remove any substring containing http
    clean_tweets[:] = [re.sub(r"^.*http.*$", '', tweet) for tweet in clean_tweets]
    # remove any non-ascii characters
    clean_tweets[:] = [re.sub(r"[^\x00-\x7F]+", '', tweet) for tweet in clean_tweets]
    # make all words lowercase
    clean_tweets[:] = [tweet.lower() for tweet in clean_tweets]
    # remove tweeter's RT' tags
    clean_tweets[:] = [tweet.replace('RT', '') for tweet in clean_tweets]
    # downloads corpus of stopwords (i.e. "the", "did", "?")
    # TODO: check if nltk.stopwords is already downloaded and if it is, then skip
    nltk.download("stopwords")
    # filtering out stop words and punctuation
    # may want to add additional filtering criteria depending upon category of tweets
    # i.e. GOP debate dataset used this filter criteria:
    #useless_ones = nltk.corpus.stopwords.words("english") + list(string.punctuation) + ['``', "''",'gop','debate','gopdeb','gopdebate','gopdebates','fox','news','foxnew','foxnews', 'amp']
    # default criteria below
    useless_ones = nltk.corpus.stopwords.words("english") + list(string.punctuation)
    # downloads work tokenizer trained on English
    # TODO: check if nltk.punkt is already downloaded and if it is, then skip
    nltk.download("punkt")
    # tokenize and clean up the whole set of clean tweet texts
    # tc_tweets = tokenized & cleaned tweets
    tc_tweets = []
    for tweet in clean_tweets:
        # creates a list of words for each tweet
        wordlist = [word for word in nltk.word_tokenize(tweet) if word not in useless_ones]
        tc_tweets.append(wordlist)
    # apply stemming algorithm to tweets
    # stemming normalizes text i.e. "waited", "waits", "waiting" -> "wait"
    # this cleans the data and makes it easier for the ML algorithm to read it
    sno = nltk.stem.SnowballStemmer("english")
    tc_tweets_stemmed = []
    for words in tc_tweets:
        stemmed_words = [sno.stem(word) for word in words]
        tc_tweets_stemmed.append(stemmed_words)
    tc_tweets[:] = tc_tweets_stemmed
    # pairs each tweet's cleaned text with its sentiment label
    text_label_pair_list = list(zip(tc_tweets, labels))
    # remove all neutral tweets since we are only interested in positive/negative ones
    text_label_pair_list[:] = [tuple for tuple in text_label_pair_list if tuple[1] != "Neutral"]
    # split into train and test set, 90% for training set, 10% for testing set
    train, test = train_test_split(text_label_pair_list, test_size = 0.1, random_state=7)
    # define bag-of-words model and features
    train_bow = [(build_bow_features(tuple[0]), tuple[1]) for tuple in train]
    test_bow = [(build_bow_features(tuple[0]), tuple[1]) for tuple in test]
    # one of the simplest supervised ML classifiers is the Naive Bayes Classifier
    # TODO: potential new tool would involve different ML classifier
    # it can be trained on 90% of the data to learn what words are associated with pos/neg comments
    sentiment_classifier = NaiveBayesClassifier.train(train_bow)
    # we can check after training what the accuracy is on the training set
    # i.e. the same data we used for training, this should be a high number since algo already saw the data
    #nltk.classify.util.accuracy(sentiment_classifier, train_bow)*100
    # accuracy on the testing set
    #nltk.classify.util.accuracy(sentiment_classifier, test_bow)*100
    test_comment_dicts, test_labels = list(zip(*test_bow))
    preds = [sentiment_classifier.classify(comment_dict) for comment_dict in test_comment_dicts]
    pred_vs_observ = pd.DataFrame(np.array([test_labels, preds]).T, columns=["observation", "prediction"])
    pred_vs_observ.transpose()
    # TODO: figure out what to return
    #return pd.Series(rxt_params).to_json(orient="records")