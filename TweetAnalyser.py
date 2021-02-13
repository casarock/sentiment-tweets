import re, string, nltk
import pandas as pd
from textblob_de import TextBlobDE as TextBlob
from nltk.corpus import stopwords
from nltk.probability import FreqDist

class TweetAnalyser:

    def __init__(self, file_name):
        """ Constructor.

        Args:
            file_name (string): Filename of csv with Tweets
        """
        self.sentiment = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }

        self.file_name = file_name
        self.tweets = None
        self.word_distribution = None

    def load_tweets(self, file_name = None):
        """ Load a CSV with tweets to be analysed

        Args:
            file_name (string, optional): Optional filename to be able to load new tweets. Defaults to None.
        """
        if file_name != None:
            self.file_name = file_name

        self.tweets = pd.read_csv(self.file_name)

    def prepare_tweets(self):
        """ Prepare Tweets and add additonal columns
        """
        self.tweets['date'] = pd.to_datetime(self.tweets['date'])
        self.tweets['cleaned'] = self.tweets['text'].apply(self.clean_tweet)
        self.tweets['sentiment'] = self.tweets['text'].apply(self.get_sentiment)

    def analyse_tweets(self):
        """ Analyse Tweets: calculate sentiment and create a wordlist.
        """
        word_list = []
        self.prepare_tweets()

        for _, tweet in self.tweets.iterrows():
            wl = self.strip_stop_words(self.lemmatize_words(tweet['cleaned']))

            word_list += wl

            if tweet['sentiment'] == 0:
                self.sentiment['neutral'] += 1
            elif tweet['sentiment'] > 0:
                self.sentiment['positive'] += 1
            else:
                self.sentiment['negative'] += 1

            # add sentiment as new column to our dataframe

        self.word_distribution = FreqDist(word_list)

    def clean_tweet(self, tweet):
        """ Clean a tweet text. Removes links and some entities.

        Args:
            tweet (string): Text of tweet which should be cleaned

        Returns:
            string: clean Tweet
        """
        # remove urls, hashtag etc.
        cleaned = self.strip_all_entities(self.strip_links(tweet))

        return cleaned

    def get_sentiment(self, tweet):
        """ get a setinement score for a specific tweet

        Args:
            tweet (string): Text of tweet

        Returns:
            float: Sentiment score
        """
        analysis = TextBlob(tweet)

        return analysis.sentiment.polarity

    def get_sentiment_results(self):
        """ Create a analysis of all sentiments in tweets.

        Returns:
            dict: a dictionary with some informations about the sentiments of tweets
        """
        sum = self.sentiment['positive'] + self.sentiment['negative'] + self.sentiment['neutral']
        percent_positive = round((100/sum)*self.sentiment['positive'])
        percent_negative = round((100/sum)*self.sentiment['negative'])
        percent_neutral = 100 - percent_negative - percent_positive

        return {
            'sum': sum,
            'p_pos': round(percent_positive),
            'p_neg': round(percent_negative),
            'p_neu': round(percent_neutral)

        }

    def strip_stop_words(self, words):
        """ remove stop words from a string of words.

        Args:
            words (list): List of words which should be cleaned

        Returns:
            list: cleaned list of words.
        """
        s_words = stopwords.words('german')
        s_words.append('Die')
        word_list = []

        for word in words:
            if word not in s_words:
                word_list.append(word)

        return word_list

    def lemmatize_words(self, text):
        """ Lemmatize a string of words

        Args:
            text (string): Text whcih should be lemmatize

        Returns:
            list: List of lemmatized words
        """
        analyse = TextBlob(text)
        wl = analyse.words.lemmatize()

        return wl

    def strip_links(self, text):
        """ Strip Links from a text

        Args:
            text (string): Text with linksto be cleaned

        Returns:
            string: Cleaned text
        """
        link_regex = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL)
        links = re.findall(link_regex, text)
        for link in links:
            text = text.replace(link[0], ', ')

        return text

    def strip_all_entities(self, text):
        """ Remove entites from a tweet (Hashtags and mentions)

        Args:
            text (string): Tweet to be cleaned

        Returns:
            string: Cleaned tweet
        """
        entity_prefixes = ['@','#']
        for separator in string.punctuation:
            if separator not in entity_prefixes :
                text = text.replace(separator,' ')
        words = []

        for word in text.split():
            word = word.strip()
            if word:
                if word[0] not in entity_prefixes:
                    words.append(word)

        return ' '.join(words)

if __name__ == "__main__":
    file_name = 'tweets.csv'
    tw_analyst = TweetAnalyser(file_name)
    tw_analyst.load_tweets()
    tw_analyst.analyse_tweets()