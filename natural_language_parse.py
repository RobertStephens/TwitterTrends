import nltk, langid

from prettytable import PrettyTable
from collections import Counter

import use_naive_bayes

#import string

class NaturalLanguageParse:

    def __init__(self, search_term): 
        print "construct NaturalLanguageParse" 
        self.use_naive_bayes = use_naive_bayes.UseNaiveBayes()
        self.search_term = search_term 
        self.en_statuses = []

        self.pos_log = open("pos_log.txt", 'a')
        self.neg_log = open("neg_log.txt", 'a')

    def load_english_statuses(self, statuses):
        for status in statuses: 
            if self.is_sentence_english( status['text'] ):
                #filter( lambda x: x in string.printable, status['text'] ) 
                self.en_statuses.append( status )

    def run_common_nouns(self):
        self.print_most_common()

    def run_is_pos_or_neg(self):
        review_map = {"pos":0, "neg":0, "na":0}
    
        for status in self.en_statuses:
            sentence = status['text']
            result = self.is_sentence_positive( sentence )
            review_map[ result ] += 1
           
            if(result == "pos"):
                self.pos_log.write(sentence.encode('utf-8') + '\n')  
            elif(result == "neg"): 
                self.neg_log.write(sentence.encode('utf-8') + '\n')  
            else:
                print "error, unknown pos/neg classification " + result 
       
        self.pos_log.close()
        self.neg_log.close()
        
        return review_map


    def parse_sentence(self, sentence): 
        
        tokens = nltk.word_tokenize( sentence )
        tagged = nltk.pos_tag( tokens )
        return tagged 
        
        '''  
        entities = nltk.chunk.ne_chunk(tagged)
        print entities
   
        from nltk.corpus import treebank
        t = treebank.parsed_sents('wsj_0001.mrg')[0]
        t.draw()
        ''' 
    
    def is_sentence_positive(self, sentence): 
        result = 'na'  
        result = self.use_naive_bayes.is_sentence_neg_pos( sentence )
        #print result  + " " + sentence
        return result

    def is_sentence_english(self, sentence):
        
        result = langid.classify( sentence )
        return result[0] == 'en'

    def print_most_common(self):
    
        status_texts = [ status['text'] for status in self.en_statuses ]
        screen_names = [ user_mention['screen_name'] for status in self.en_statuses for user_mention in status['entities']['user_mentions'] ]
        hashtags = [ hashtag['text'] for status in self.en_statuses for hashtag in status['entities']['hashtags'] ]
        
        '''   
        words = [ w for t in status_texts for w in t.split() ]
        ''' 
        
        # Compute a collection of all nouns from all tweets
        noun_words = []  
        for sentence in status_texts:
            noun_words += self.remove_non_nouns( sentence ) 
        
        words_pared = self.remove_common_twitter_words( noun_words )
         
        from prettytable import PrettyTable
    
        for label, data in (('Word', words_pared),
                            ('Screen Name', screen_names),
                            ('Hashtag', hashtags)):
            pt = PrettyTable(field_names=[label, 'Count'])
            c = Counter(data)
            [ pt.add_row(kv) for kv in c.most_common()[:10] ]
            pt.align[label], pt.align['Count'] = 'l', 'r' # Set column alignment
            print pt

    def remove_common_twitter_words( self, words ):
    
        words_pared = []
        common_twitter_words = ["rt", "follow", "gain", "i", "who", "followers", "this", "me", "the", "http", "@"]
   
        common_twitter_words.append( self.search_term.lower() ) 
        
        for word in words:
            if word not in common_twitter_words:
                words_pared.append( word )
    
        return words_pared
    
    def remove_non_nouns( self, sentence_in ):
        tags = self.parse_sentence( sentence_in )
        nouns = [tag[0].lower() for tag in tags if tag[1][0:2] == "NN"]
        return nouns 




