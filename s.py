#!/usr/bin/env python
# encoding: utf-8
"""
s.py

Created by Hilary Mason on 2010-08-15.
Copyright (c) 2010 Hilary Mason. All rights reserved.
"""


import sys, os
import re
import datetime
from optparse import OptionParser

import pymongo

import settings
from lib import mongodb
from lib import display


class Search(object):
    def __init__(self, options, args):
        self.db = mongodb.connect('tweets')
        tweets = self.tweet_search(args, options.num)
        d = display.Display()
        d.display_tweets(tweets)
        
        
    def tweet_search(self, query_terms, num=10):
        r = re.compile(' '.join(query_terms), re.I)
        tweets = []
        for t in self.db['tweets'].find(spec={'text': r }).sort('created_at',direction=pymongo.DESCENDING):
            t['_display'] = True
            t['_datetime'] = datetime.datetime.strftime(t['created_at'], "%I:%M%p, %b %d, %Y %Z")
            tweets.append(t)
            
        return tweets[:num]
    
    
    
if __name__ == "__main__":
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False, help="set debug mode = True")
    parser.add_option("-n", "--num", dest="num", action="store", default=10, help="number of tweets to retrieve")
    # parser.add_option("-t", "--topic", dest="topic", action="store", default=None, help="show one topic only")
    (options, args) = parser.parse_args()

    t = Search(options, args)