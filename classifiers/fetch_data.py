import sys, os
import tweepy
from optparse import OptionParser

sys.path.append('..')
import settings


if __name__ == '__main__':
    parser = OptionParser("usage: %prog [options]") # no args this time
    # parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False, help="set debug mode = True")
    parser.add_option("-q", "--query", dest="query", action="store", help="query")
    (options, args) = parser.parse_args()
    
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
    api = tweepy.API(auth)
    
    for t in api.search(options.query, lang='en', rpp=100):
        try:
            print "%s %s" % (t.from_user, t.text)
        except UnicodeEncodeError:
            pass