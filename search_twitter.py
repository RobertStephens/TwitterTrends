#! /usr/bin/env python

import twitter
import sys, json
import natural_language_parse

def search_twitter( search_term ):
    count = 100
    no_batches = 5 
    
    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets
    search_results = twitter_api.search.tweets(q=search_term, count=count)
    statuses = search_results['statuses']
    
    # Iterate through no_batches more batches of results by following the cursor
    for _ in range(no_batches):
        print "Length of statuses", len(statuses)
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e: # No more results when next_results doesn't exist
            break
            
        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])
        
        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']
    
    return statuses


def print_results( statuses ):
    for status in statuses:
        print status['text']


if __name__ == "__main__":

    # XXX: Go to http://dev.twitter.com/apps/new to create an app and get values
    # for these credentials, which you'll need to provide in place of these
    # empty string values that are defined as placeholders.
    # See https://dev.twitter.com/docs/auth/oauth for more information 
    # on Twitter's OAuth implementation.
  
    with open("twitter_key_data.txt") as f:
        CONSUMER_KEY_TEMP = f.readline().split('=')[1].strip()
        CONSUMER_SECRET_TEMP = f.readline().split('=')[1].strip()
        OAUTH_TOKEN_TEMP = f.readline().split('=')[1].strip()
        OAUTH_TOKEN_SECRET_TEMP = f.readline().split('=')[1].strip()
   
    CONSUMER_KEY       = CONSUMER_KEY_TEMP
    CONSUMER_SECRET    = CONSUMER_SECRET_TEMP
    OAUTH_TOKEN        = OAUTH_TOKEN_TEMP
    OAUTH_TOKEN_SECRET = OAUTH_TOKEN_SECRET_TEMP

    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
    
    twitter_api = twitter.Twitter(auth=auth)
 
 
    if( len(sys.argv) != 2 ):
        search_term = '#Rosetta' 
    else: 
        search_term = sys.argv[1] 

    print "search for " + search_term  + " ..."
    
    statuses = search_twitter(search_term)

    lang_parse = natural_language_parse.NaturalLanguageParse( search_term )
    lang_parse.load_english_statuses( statuses )
    lang_parse.run_common_nouns()

    review_map = lang_parse.run_is_pos_or_neg()
    print review_map



