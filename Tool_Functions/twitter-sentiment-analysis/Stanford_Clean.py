import json
import pandas as pd
import nltk
import re

# ref: https://blog.chapagain.com.np/python-nltk-twitter-sentiment-analysis-natural-language-processing-nlp/
emoticons_happy = [':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
    ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
    '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
    'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
    '<3']
emoticons_sad = [':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
    ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
    ':c', ':{', '>:\\', ';(', ':\/', ':((']

emoticonPunctuation = emoticons_happy + emoticons_sad

def cleanTweet(tweet):
    ret = ''
    for word in tweet.split(' '):
        if word not in emoticonPunctuation:
            ret += word + ' '
    # make lowercase
    ret = ret.lower()
    # remove all newlines from inside strings
    ret = ret.replace('\n', "").strip()
    # remove unicode left/right quote characters
    ret = ret.replace(u'\u2018', '\'').replace(u'\u2019', '\'')
    # convert abbreviations
    # i.e. couldn't -> could not
    ret = ret.replace("n\'t", " not")
    # remove any non-ascii characters
    ret = re.sub(r"[^\x00-\x7F]+", "", ret)
    # remove stock market tickers
    ret = re.sub(r"\$\w*", "", ret)
    # remove old-school retweet text RT
    ret = re.sub(r"^RT[\s]+", "", ret)
    # remove hyperlinks
    ret = re.sub(r"https?:\/\/.*[\r\n]*", "", ret)
    # remove hashtags
    ret = re.sub(r"#", "", ret)
    # remove @
    ret = ret.replace('@', "")
    return ret

def main(twtInfo:object):
    data = pd.read_json(twtInfo, orient="records", lines=True)
    data_tweets = data["text"]
    data_id = data["id"]
    clean_data_tweets = [cleanTweet(tweet) for tweet in data_tweets]
    ret = []
    for i in range(len(clean_data_tweets)):
        ret.append({})
        ret[i]["text"] = clean_data_tweets[i]
        ret[i]["id"] = data_id[i]
    return pd.Series(ret).to_json(orient="records")

