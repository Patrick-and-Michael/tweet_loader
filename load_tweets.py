import json
import os
import requests
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler

TRUMPTWEETS_URL = 'https://intense-tor-73147.herokuapp.com'

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

sched = BlockingScheduler()

def initiate_tweepy_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def get_newest_oldest():
    response = requests.get('/'.join([TRUMPTWEETS_URL, 'api/tweetloader']))
    if response.status_code != 200:
        return 0, 0
    try:
        data = response.json()
    except json.decoder.JSONDecodeError:
        return 0, 0
    return data['newest'], data['oldest']


@sched.scheduled_job('interval', minutes=1)
def load_tweets():
    print('starting job...')
    newest, oldest = get_newest_oldest()
    api = initiate_tweepy_api()
    trump = api.get_user('realDonaldTrump')
    if newest < trump.status.id:
        tweets = tweepy.Cursor(api.user_timeline,
                               id=trump.id,
                               since_id=newest).items()
        print('got newer tweets')
    else:
        tweets = tweepy.Cursor(api.user_timeline,
                               id=trump.id,
                               max_id=oldest).items()
        print('got older tweets')
    payload = {'statuses': []}
    for s in tweets:
        d = {}
        d['raw_text'] = s.text
        d['author_name'] = s.author.name
        d['author_id'] = s.author.id
        d['created_at'] = str(s.created_at)
        d['tweet_id'] = s.id
        payload['statuses'].append(d)

    print('count: {}'.format(len(payload['statuses'])))

    requests.post('https://intense-tor-73147.herokuapp.com/api/tweetloader', json=payload)
    print('posted tweets to primary app')


if __name__ == '__main__':
    print('starting...')
    sched.start()
