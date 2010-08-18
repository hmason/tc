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

import settings
from lib import mongodb
from lib import display    

class Twitter(object):
    def __init__(self, options):
        self.settings = self.load_settings()
        self.db = mongodb.connect('tweets')
                
        tweets = self.load_tweets(int(options.num), sort=options.sort, mark_read=options.mark_read)
        d = display.Display()
        d.display_tweets(tweets)
        
        
    def load_tweets(self, num, sort='time',mark_read=True):
        tweets = []
        
        if sort == 'antitime': # sort by time, oldest first
            for t in self.db['tweets'].find(spec={'r': {'$exists': False } }).sort('created_at',direction=pymongo.ASCENDING).limit(num):
                t['_display'] = True # mark all for display, so optimistic
                tweets.append(t)
        elif sort == 'rel':
            for t in self.db['tweets'].find(spec={'r': {'$exists': False } }).sort('created_at',direction=pymongo.ASCENDING): # get all unread tweets
                t['_display'] = True
                tweets.append(t)
            tweets = self.sort_by_relevance(tweets, num=num)
        elif sort == 'inf':
            for t in self.db['tweets'].find(spec={'r': {'$exists': False } }).sort('created_at',direction=pymongo.ASCENDING): # get all unread tweets
                t['_display'] = True
                tweets.append(t)
            tweets = self.sort_by_influence(tweets, num=num)
        else: # sort by time, newest first
            for t in self.db['tweets'].find(spec={'r': {'$exists': False } }).sort('created_at',direction=pymongo.DESCENDING).limit(num):
                t['_display'] = True
                tweets.append(t)
    
        # mark these tweets as 'read' in the db
        if mark_read:
            for t in tweets:
                self.db['tweets'].update({'_id': t['_id']}, {'$set': {'r': 1 }})


        # black/white lists
        for t in tweets:
            if t['user'] in self.settings['blacklist_users']:
                t['_display'] = False
                
            for blackword in self.settings['blacklist']:
                if blackword.search(t['text'].lower()):
                    t['_display'] = False
            
            t['_display_topics'] = []
            try:
                for topic, score in t['topics'].items():
                    # print "topic: %s, score: %s" % (topic, score)
                    # print "threshold: %s" % self.settings['topic_thresholds'][topic]
                    if score >= self.settings['topic_thresholds'][topic]:
                        t['_display_topics'].append(topic) 
            except KeyError: # no topic analysis for this tweet
                pass
                    
            if t['user'] in self.settings['whitelist_users']:
                t['_display'] = True
                
        # cache any links in these tweets so I can get to them easily
        self.extract_links(tweets)
                    
        return tweets
    
    def sort_by_influence(self, tweets, num):
        """
        sort_by_influence: sort tweets by klout score
        """
        for t in tweets:
            for k in self.db['users'].find(spec={'_id':t['author']}, fields={'klout_score': True}):
                try:
                    t['influence'] = k['klout_score']
                except KeyError: # no klout score
                    t['influence'] = 0

        return sorted(tweets, key=lambda x:-x['influence'])[:num]
        
    def sort_by_relevance(self, tweets, num):
        """
        sort_by_relevance: sorts tweets by arbitrary relevance to me. Criteria:
        1) does it mention me?
        2) is it by someone on my whitelist?
        3) is it about a topic that I care about?
        4) sort remainder by 'interestingness'
        """
        mentions = []
        whitelist = []
        topical = []
        other = []
        
        for t in tweets:
            t['_display_topics'] = []
            try:
                for topic, score in t['topics'].items():
                    if score >= self.settings['topic_thresholds'][topic]:
                        t['_display_topics'].append(topic) 
            except KeyError:
                pass

            if settings.TWITTER_USERNAME in t['text']:
                mentions.append(t)
            elif t['user'] in self.settings['whitelist_users']:
                whitelist.append(t)
            elif t['_display_topics']:
                topical.append(t)
            else:
                other.append(t)

        tweets = mentions + whitelist + topical + other
        
        return tweets[:num]
        
        
    def extract_links(self, tweets):
        """
        extract_links: pull links out of tweets and cache in a text file
        """
        re_http = re.compile("(http|https):\/\/(([a-z0-9\-]+\.)*([a-z]{2,5}))\/[\w|\/]+")
        links = []
        for t in tweets:
            r = re_http.search(t['text'])
            if r:
                links.append(r.group(0))
        
        if links:
            f = open(self.settings['link_cache_filename'], 'w')
            for link in links:
                f.write('%s\n' % link)
            f.close()
        
        
    def load_settings(self):
        settings = {}
        
        settings['topic_thresholds'] = {'default': .6, 'betaworks': 1.0, 'narcissism': .25, 'sports': .9999 }
        settings['link_cache_filename'] = 'link_cache'
        
        f = open('whitelist_users', 'r')
        settings['whitelist_users'] = [user.strip() for user in f.readlines()]
        f.close()

        f = open('blacklist_users', 'r')
        settings['blacklist_users'] = [user.strip() for user in f.readlines()]
        f.close()
        
        f = open('blacklist', 'r')
        settings['blacklist'] = [re.compile(b.lower().strip()) for b in f.readlines()]
        f.close()
        
        return settings

if __name__ == "__main__":
    parser = OptionParser("usage: %prog [options]") # no args this time
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False, help="set debug mode = True")
    parser.add_option("-m", "--mark_read", dest="mark_read", action="store_false", default=True, help="Don't mark displayed tweets as read")
    parser.add_option("-s", "--sort", dest="sort", action="store", default='time', help="Sort by time, antitime, rel")
    parser.add_option("-n", "--num", dest="num", action="store", default=10, help="number of tweets to retrieve")
    # parser.add_option("-t", "--topic", dest="topic", action="store", default=None, help="show one topic only")
    (options, args) = parser.parse_args()
    
    t = Twitter(options)