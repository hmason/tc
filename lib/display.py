import sys, os

sys.path.append('..')
import settings

class Display(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    ITAL_ON = '\033[3m'
    ITAL_OFF = '\033[23m'
    BOLD_ON = '\033[1m'
    BOLD_OFF = '\033[22m'
    
    MAX_TWITTER_USERNAME_LENGTH = 15
    
    def display_tweets(self, tweets):

        for t in tweets:
            if t['_display']:
                spacer = ' '.join(['' for i in range((self.MAX_TWITTER_USERNAME_LENGTH + 2) - len(t['user']))])
                if settings.TWITTER_USERNAME in t['text']: # highlight replies   
                    t['text'] = self.BOLD_ON + t['text'] + self.BOLD_OFF
                tweet_text = self.OKGREEN + t['user'] + self.ENDC + spacer + t['text']
                if t.get('_display_topics', None): # print with topics
                    print tweet_text + '  ' + self.OKBLUE + ' '.join(t['_display_topics']) + self.ENDC
                if t.get('_datetime', None): # print with date/time
                    print tweet_text + '  ' + self.OKBLUE + t['_datetime'] + self.ENDC
                else: # print without topics
                    print tweet_text

    def display_users(self, users):

        for t in users:
            if t['_display']:
                spacer = ' '.join(['' for i in range((self.MAX_TWITTER_USERNAME_LENGTH + 2) - len(t['_id']))])
                tweet_text = self.OKGREEN + t['_id'] + self.ENDC + spacer + t['name'] + '  ' + t['location'] + '  ' + t['description']
                if t.get('url', None): # print with url
                    print tweet_text + '  ' + self.OKBLUE + t['url'] + self.ENDC
                else: # print without topics
                    print tweet_text
    