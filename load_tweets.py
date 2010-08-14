#!/usr/bin/env python
# encoding: utf-8
"""
load_tweets.py

Created by Hilary Mason on 2010-04-25.
Copyright (c) 2010 Hilary Mason. All rights reserved.
"""

import sys, os
import datetime
import pymongo
import tweepy # Twitter API class: http://github.com/joshthecoder/tweepy
from lib import mongodb
from lib import klout
from classifiers.classify_tweets import *
import settings # local app settings

class loadTweets(object):
    DB_NAME = 'tweets'
    USER_COLL_NAME = 'users'
    
    def __init__(self, debug=False):
        self.debug = debug
        self.db = mongodb.connect(self.DB_NAME)
        self.api = self.init_twitter(settings.TWITTER_USERNAME, settings.TWITTER_PASSWORD)

        last_tweet_id = self.get_last_tweet_id()
        self.fetchTweets(last_tweet_id)
        self.classify_tweets()
        

    def get_last_tweet_id(self):
        for r in self.db[self.DB_NAME].find(fields={'id': True}).sort('id',direction=pymongo.DESCENDING).limit(1):
            return r['id']

    def fetchTweets(self, since_id=None):
        if since_id:
            tweets = self.api.home_timeline(since_id, count=500)
        else:
            tweets = self.api.home_timeline(count=500)
        
        # parse each incoming tweet
        ts = []
        authors = []
        for tweet in tweets: 
            t = {
            'author': tweet.author.screen_name,
            'contributors': tweet.contributors,
            'coordinates': tweet.coordinates,
            'created_at': tweet.created_at,
            # 'destroy': tweet.destroy,
            # 'favorite': tweet.favorite,
            'favorited': tweet.favorited,
            'geo': tweet.geo,
            'id': tweet.id,
            'in_reply_to_screen_name': tweet.in_reply_to_screen_name,
            'in_reply_to_status_id': tweet.in_reply_to_status_id,
            'in_reply_to_user_id': tweet.in_reply_to_user_id,
            # 'parse': tweet.parse,
            # 'parse_list': tweet.parse_list,
            'place': tweet.place,
            # 'retweet': dir(tweet.retweet),
            # 'retweets': dir(tweet.retweets),
            'source': tweet.source,
            # 'source_url': tweet.source_url,
            'text': tweet.text,
            'truncated': tweet.truncated,
            'user': tweet.user.screen_name,
            }
            u = {
            '_id': tweet.author.screen_name, # use as mongo primary key
            'contributors_enabled': tweet.author.contributors_enabled, 
            'created_at': tweet.author.created_at, 
            'description': tweet.author.description, 
            'favourites_count': tweet.author.favourites_count, # beware the british
            'follow_request_sent': tweet.author.follow_request_sent, 
            'followers_count': tweet.author.followers_count, 
            'following': tweet.author.following, 
            'friends_count': tweet.author.friends_count, 
            'geo_enabled': tweet.author.geo_enabled, 
            'twitter_user_id': tweet.author.id, 
            'lang': tweet.author.lang, 
            'listed_count': tweet.author.listed_count, 
            'location': tweet.author.location, 
            'name': tweet.author.name, 
            'notifications': tweet.author.notifications, 
            'profile_image_url': tweet.author.profile_image_url, 
            'protected': tweet.author.protected, 
            'statuses_count': tweet.author.statuses_count, 
            'time_zone': tweet.author.time_zone, 
            'url': tweet.author.url, 
            'utc_offset': tweet.author.utc_offset, 
            'verified': tweet.author.verified,
            '_updated': datetime.datetime.now(),
            }
            authors.append(u)
            ts.append(t)

        self.update_authors(authors)
        
        # insert into db
        try:
            self.db[self.DB_NAME].insert(ts)
        except pymongo.errors.InvalidOperation: # no tweets?
            pass
        
        if self.debug:
            print "added %s tweets to the db" % (len(ts))

    def update_authors(self, authors):
        k = klout.KloutAPI(settings.KLOUT_API_KEY)
        update_count = 0
        
        for user in authors:
            records = [r for r in self.db[self.USER_COLL_NAME].find(spec={'_id': user['_id']})]
            if not records or abs(records[0]['_updated'] - datetime.datetime.now()) >= datetime.timedelta(1): # update once per day
                kwargs = { 'users': user['_id'] }
                response = k.call('klout', **kwargs)
                user['klout_score'] = response['users'][0]['kscore']
                self.db[self.USER_COLL_NAME].remove({'_id': user['_id']})
                self.db[self.USER_COLL_NAME].insert(user)
                update_count += 1

        if self.debug:
            print "updated %s users in the db" % (update_count)

            

    def classify_tweets(self):
        classifiers = []
        for active_classifier in active_classifiers:
            c = globals()[active_classifier]()
            classifiers.append(c)

        for r in self.db[self.DB_NAME].find(spec={'topics': {'$exists': False } },fields={'text': True, 'user': True}): # for all unclassified tweets
            topics = {}
            for c in classifiers:
                (topic, score) = c.classify(r['text'])
                topics[topic] = score

            self.db[self.DB_NAME].update({'_id': r['_id']}, {'$set': {'topics': topics }})

    
    # util classes    
    def init_twitter(self, username, password):
        auth = tweepy.BasicAuthHandler(username, password)
        api = tweepy.API(auth)
        return api


if __name__ == '__main__':
    l = loadTweets(debug=True)