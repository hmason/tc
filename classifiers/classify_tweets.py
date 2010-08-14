from __future__ import division
import sys, os, random
import nltk, re
from nltk.tokenize import *
import pickle

active_classifiers = ['betaworks', 'narcissism', 'sports', 'checkin']

class tweetClassifier(object):
    def __init__(self):
        pass

    def load_data(self, categories):
        """
        load_data: load a document line by line
        """
        data = []
        for category in categories:
            f = open('classifiers/data/%s' % category, 'r')
            for line in f.readlines():
                data.append((line, category))
        return data # returns a list of tuples of the form (line of text, category)
        
    def document_features(self, document):
        """
        document_features: this breaks a text document into the comparison set of features
        """
        document_words = set(word_tokenize(document)) # break the text down into a set (for speed) of individual words
        features = {}
        for word in self.word_features:
            features['contains(%s)' % word] = (word in document_words) # feature format follows canonical example
        return features

    def print_classification(self, classifier, line):
        """
        print_classification: Given a trained classifer and a line of text, it prints the probability that the text falls into each category
        """
        print "Content: %s" % line
        line_prob = classifier.prob_classify(self.document_features(line)) # get the probability for each category
        for cat in line_prob.samples():
            print "prob. %s = %s" % (cat, line_prob.prob(cat))
        
        

class sports(tweetClassifier):
    SAMPLE_SIZE = 500
    CLASSIFIER_DUMP = 'classifiers/trained/sports'
    
    def __init__(self, debug=False):
        self.debug = debug
        
        try:
            (self.classifier, self.word_features) = pickle.load(open(self.CLASSIFIER_DUMP, 'r'))
        except IOError:
            data = self.load_data(['sports', 'new_york'])
            self.train_classifier(data)
            pickle.dump((self.classifier, self.word_features), open(self.CLASSIFIER_DUMP, 'w'))
                    
        
    def train_classifier(self, data):
        data = random.sample(data, self.SAMPLE_SIZE)

        all_words = [] # build a freq distribution of all words used in all documents in the dataset
        for line,cat in data:
            all_words.extend(word_tokenize(line))
        all_words = [word for word in all_words if len(word) > 2] # filter out very short words
        all_words_freq = nltk.FreqDist(w.lower() for w in all_words) # frequency distribution is a dist of the form word: count_of_how_often_word_appears
        self.word_features = all_words_freq.keys()[:1000] # use the 2k most freq words as our set of features

        featuresets = [(self.document_features(d), c) for (d,c) in data] # divide data into testing and training sets
        train_set, test_set = featuresets[200:], featuresets[:200]

        self.classifier = nltk.NaiveBayesClassifier.train(train_set) # invoke the naive bayesian classifier

        if self.debug:
            print "training new sports classifier"
            print "Accuracy of the classifier: %s" % nltk.classify.accuracy(self.classifier, test_set) # print the accuracy of the classifier

        # classifier.show_most_informative_features(100) # show the features that have high relevance
    
        
    def classify(self, tweet):
        line_prob = self.classifier.prob_classify(self.document_features(tweet)) # get the probability for each category
        return ('sports', line_prob.prob('sports'))

        
class narcissism(tweetClassifier):
    N_THRESHOLD = 5.0
    
    def __init__(self):
        self.keywords = ['my latest', 'out my', 'my new', 'i am', 'i hate', 'i love', 'i like', "i can't", 'new post', 'did i', 'i shall', 'i really', 'i wish', 'mine', "i'll", 'i do', "i don't", "i won't", "for my", "i did", "i have", "i had", 'fml']
        
    def classify(self, tweet):
        count = 0
        for word in self.keywords:
            if word in tweet.lower():
                count += 1
                
        score = min((float(count) / self.N_THRESHOLD), 1.0) # max score = 1.0
        return ('narcissism', score)
        
class betaworks(tweetClassifier):
    def __init__(self):
        self.keywords = ['tweetdeck', 'chartbeat', 'socialflow', '@bitly', 'venmo', 'tumblr', 'superfeedr', 'backupify', 'fluiddb', 'twitterfeed']
        
    def classify(self, tweet):
        score = 0.0
        for word in self.keywords:
            if word in tweet.lower():
                score = 1.0
                
        return ('betaworks', score)

class checkin(tweetClassifier):
    def __init__(self):
        self.keywords = ['4sq.com']

    def classify(self, tweet):
        score = 0.0
        for word in self.keywords:
            if word in tweet.lower():
                score = 1.0

        return ('checkin', score)

        
if __name__ == '__main__':
    # n = narcissism()
    # print n.classify("I like marshamllowdkjfdk my mine my new i hate i am")
    s = sports(debug=True)
    print s.classify("#Dolphins WR Brandon Marshall says he plans to pursue NBA career if NFL teams lock out their players.")
    print s.classify("Open mapping potentials for humanitarian response by @rrbaker #isb2")