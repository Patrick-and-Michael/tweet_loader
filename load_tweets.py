import requests
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler

TRUMPTWEETS_URL = 'https://intense-tor-73147.herokuapp.com'

CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

sched = BlockingScheduler()

def initiate_tweepy_api():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def get_newest_oldest():
    response = requests.get('/'.join([URL, 'newest-oldest']))
    data = response.json()
    return data['newest'], data['oldest']


@sched.scheduled_job('interval', minutes=10)
def load_tweets():
    newest, oldest = get_newest_oldest()
    api = initiate_tweepy_api()
    trump = api.get_user("realDonaldTrump")

sched.start()
