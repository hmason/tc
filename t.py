#!/usr/bin/env python
# encoding: utf-8
"""
t.py

Created by Hilary Mason on 2010-04-25.
Copyright (c) 2010 Hilary Mason. All rights reserved.
"""

import sys, os
import re
from optparse import OptionParser

import pymongo
import tweepy

from lib import mongodb
from lib import display    

class Twitter(object):
    def __init__(self, options):
        self.settings = self.load_settings()
        self.db = mongodb.connect('tweets')
                
        tweets = self.load_tweets(int(options.num))
        self.display_tweets(tweets)
        
    def display_tweets(self, tweets):
        d = display.Display()
        
        for t in tweets:
            spacer = ' '.join(['' for i in range((d.MAX_TWITTER_USERNAME_LENGTH + 2) - len(t['user']))])
            print d.OKGREEN + t['user'] + d.ENDC + spacer + t['text']
        
    def load_tweets(self, num, sort='time'):
        tweets = []
        
        if sort == 'time':
            for t in self.db['tweets'].find(spec={'r': {'$exists': False } }).sort('created_at',direction=pymongo.DESCENDING).limit(num):
                t['_display'] = True # mark all for display, so optimistic
                tweets.append(t)
    
        # mark these tweets as 'read' in the db
        # for t in tweets:
        #     self.db['tweets'].update({'_id': t['_id']}, {'$set': {'r': 1 }})


        # black/white lists
        for t in tweets:
            if t['user'] in self.settings['blacklist_users']:
                t['_display'] = False
                
            for blackword in self.settings['blacklist']:
                if blackword.search(t['text'].lower()):
                    t['_display'] = False
                    
            if t['user'] in self.settings['whitelist_users']:
                t['_display'] = True
                    
        return tweets
        
    def load_settings(self):
        settings = {}
        
        f = open('whitelist_users', 'r')
        settings['whitelist_users'] = [user.strip() for user in f.readlines()]
        f.close()

        f = open('blacklist_users', 'r')
        settings['blacklist_users'] = [user.strip() for user in f.readlines()]
        f.close()
        
        f = open('blacklist', 'r')
        settings['blacklist'] = [re.compile(b.lower()) for b in f.readlines()]
        f.close()
        
        return settings

if __name__ == "__main__":
    parser = OptionParser("usage: %prog [options]") # no args this time
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False, help="set debug mode = True")
    parser.add_option("-s", "--sort", dest="sort", action="store", default='time', help="Sort by time, rel")
    parser.add_option("-n", "--num", dest="num", action="store", default=10, help="number of tweets to retrieve")
    parser.add_option("-t", "--topic", dest="topic", action="store", default=None, help="show one topic only")
    (options, args) = parser.parse_args()
    
    t = Twitter(options)