#!/usr/bin/env python
# encoding: utf-8
"""
w.py

Created by Hilary Mason on 2010-08-21.
"""

import sys, os
from optparse import OptionParser
import pickle

import tweepy

import settings
from lib import mongodb


class writeTweet(object):
    def __init__(self, options, args):
        if options.debug:
            print options
            print args
        
        auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
        self.api = tweepy.API(auth)
        tweet = args[0]
        self.post_tweet(tweet)
        
    def post_tweet(self, tweet):
        self.api.update_status(tweet)
    
    
    
if __name__ == '__main__':
    parser = OptionParser("usage: %prog [options] [tweet]") # no args this time
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False, help="set debug mode = True")
    (options, args) = parser.parse_args()

    l = writeTweet(options, args)