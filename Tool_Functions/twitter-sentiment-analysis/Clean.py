import json
import pandas as pd
import nltk

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