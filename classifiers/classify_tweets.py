from __future__ import division
import sys, os, random

active_classifiers = ['betaworks', 'narcissism']

class tweetClassifier(object):
    def __init__(self):
        pass
        
class narcissism(tweetClassifier):
    N_THRESHOLD = 4.0
    def __init__(self):
        self.keywords = ['out my', 'my new', 'i am', 'i hate', 'i love', 'i like', "i can't", 'new post', 'did i', 'i shall', 'i really', 'i wish', 'mine']
        
    def classify(self, tweet):
        count = 0
        for word in self.keywords:
            if word in tweet.lower():
                count += 1
                
        score = min((float(count) / self.N_THRESHOLD), 1.0) # max score = 1.0
        return ('narcissism', score)
        
class betaworks(tweetClassifier):
    def __init__(self):
        self.keywords = ['tweetdeck', 'chartbeat', 'socialflow', '@bitly']
        
    def classify(self, tweet):
        score = 0.0
        for word in self.keywords:
            if word in tweet.lower():
                score = 1.0
                
        return ('betaworks', score)
        
if __name__ == '__main__':
    n = narcissism()
    print n.classify("I like marshamllowdkjfdk my mine my new i hate i am")