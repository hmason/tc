
# configure me!
TWITTER_USERNAME = ''

# you shouldn't need to touch

import pickle

CONSUMER_KEY = 'KYQAsPtHu09IzYpoQesZvA'
CONSUMER_SECRET = '3afLbAvMNFhsNLK6OcqxBjKSjD3hGaPKgXgFV38Ug'

KLOUT_API_KEY = 'p4ccneaqr32tjyygjgg25cm2'

try:
    (ACCESS_KEY, ACCESS_SECRET) = pickle.load(open('settings_twitter_creds'))
except IOError:
    (ACCESS_KEY, ACCESS_SECRET) = ('', '')