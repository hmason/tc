# From: http://code.google.com/p/python-klout/

from datetime import date, timedelta

import time
import urllib
import urllib2

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        try:
            from django.utils import simplejson as json
        except:
            raise 'Requires either Python 2.6 or above, simplejson or django.utils!'

RETRY_COUNT = 5
API_BASE_URL = 'http://api.klout.com/1/'

#
# NOTE: some verbs are disabled as they are still under development
# and currently don't work with the API
# 
VERB_PARAMS = {
    'klout': [
        'users'
    ],
    'soi.influenced_by': [
        'users'
    ],
    'soi.influencer_of': [
        'users'
    ],
    # 'topics.search': [
    #     'topic'
    # ],
    # 'topics.verify': [
    #     'topic'
    # ],
    # 'users.history': [
    #     'end_date',
    #     'start_date',
    #     'users'
    # ],
    'users.show': [
        'users'
    ],
    # 'users.stats': [
    #     'users'
    # ],
    'users.topics': [
        'users'
    ],
}


class KloutError( Exception ):
    """
    Base class for Klout API errors.
    """
    @property
    def message( self ):
        """
        Return the first argument passed to this class as the message.
        """
        return self.args[ 0 ]
    
    
class KloutAPI( object ):
    def __init__( self, api_key ):
        self.api_key = api_key
        self._urllib = urllib2
        
    def call( self, verb, **kwargs ):
        # build request
        request = self._buildRequest( verb, **kwargs )

        # fetch data
        result = self._fetchData( request )

        # return result
        return result
    
    def _buildRequest( self, verb, **kwargs ):
        # add API key to all requests
        params = [
            ( 'key', self.api_key ),
        ]

        # check params based on the given verb and build params
        for k, v in kwargs.iteritems():
            if k in VERB_PARAMS[ verb ]:
                params.append( ( k , v ) )
            else:
                raise KloutError(
                        "Invalid API parameter %s for verb %s" % ( k, verb ) )

        # encode params
        encoded_params = urllib.urlencode( params )
        
        # URL to API endpoint
        url = '%s/%s.json?%s' % ( API_BASE_URL, verb.replace( '.', '/' ), 
            encoded_params )
        
        # build request and return it
        request = urllib2.Request( url )
        return request
    
    def _fetchData( self, request ):
        counter = 0
        while True:
            try:
                if counter > 0:
                    time.sleep( counter * 0.5 )
                url_data = self._urllib.urlopen( request ).read()
                json_data = json.loads( url_data )
            except urllib2.HTTPError, e:
                if e.code == 400:
                    raise KloutError(
                        "Klout sent status %i:\ndetails: %s" % (
                            e.code, e.fp.read() ) )
                counter += 1
                if counter > RETRY_COUNT:
                    raise KloutError(
                        "Klout sent status %i:\ndetails: %s" % (
                            e.code, e.fp.read() ) )
            except ValueError:
                counter += 1
                if counter > RETRY_COUNT:
                    raise KloutError(
                        "Klout did not return valid JSON data" )
            else:
                return json_data


if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter( indent = 4 )
    
    verb_list = VERB_PARAMS.keys()
    verb_list.sort()

    users = 'biz,mashable'
    topic = 'iPhone'
    start_date = date.today() - timedelta( days = 6 )
    end_date = date.today()
    
    a = KloutAPI( api_key = 'v4rexwayms7kumxgqgh57nhx' )
    
    for verb in verb_list:
        print 'Testing verb: %s' % ( verb )
        if verb in [ 'topics.search', 'topics.verify' ]:
            kwargs = { 'topic': topic }
        else:
            kwargs = { 'users': users }
        x = a.call( verb, **kwargs )
        pp.pprint( x )