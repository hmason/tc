#!/usr/bin/env python
# encoding: utf-8
"""
tweetbc.py

Created by Hilary Mason on 2010-04-25.
Copyright (c) 2010 Hilary Mason. All rights reserved.
"""

import sys, os
import pymongo
import tweepy # Twitter API class: http://github.com/joshthecoder/tweepy


class tweetBC(object):
    TWITTER_USERNAME = 'bc_l' # configure me
    TWITTER_PASSWORD = 'XXX' # configure me
    DM_CACHE = 'last_seen.txt' # possibly configure me
    
    def __init__(self):
        api = self.init_twitter(self.TWITTER_USERNAME, self.TWITTER_PASSWORD)


if __name__ == '__main__':
    pass