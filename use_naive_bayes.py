#! /usr/bin/env python

import re, math, collections, itertools, os
import nltk, nltk.classify.util, nltk.metrics
from nltk.classify import NaiveBayesClassifier
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist


POLARITY_DATA_DIR = os.path.join('polarity_data', 'rt-polaritydata')
RT_POLARITY_POS_FILE = os.path.join(POLARITY_DATA_DIR, 'rt-polarity-pos.txt')
RT_POLARITY_NEG_FILE = os.path.join(POLARITY_DATA_DIR, 'rt-polarity-neg.txt')
TEST_POLARITY_POS_FILE = os.path.join(POLARITY_DATA_DIR, 'test-polarity-pos.txt')
TEST_POLARITY_NEG_FILE = os.path.join(POLARITY_DATA_DIR, 'test-polarity-neg.txt')


class UseNaiveBayes:

    def __init__(self):
        print "init UseNaiveBayes"    
        self.train_words(self.make_full_dict)
    
    def test_trained(self, testFeatures ):
        #initiates referenceSets and testSets
        referenceSets = collections.defaultdict(set)
        testSets = collections.defaultdict(set)    
    
        #puts correctly labeled sentences in referenceSets and the predictively labeled version in testsets
        for i, (features, label) in enumerate(testFeatures):
            referenceSets[label].add(i)
            predicted = self.classifier.classify(features)
            #print "test trained " + " ".join( features ) + " result: " + predicted
            testSets[predicted].add(i)    
    
        #prints metrics to show how well the feature selection did
        print 'accuracy:', nltk.classify.util.accuracy(self.classifier, testFeatures)
        print 'pos precision:', nltk.metrics.precision(referenceSets['pos'], testSets['pos'])
        print 'pos recall:', nltk.metrics.recall(referenceSets['pos'], testSets['pos'])
        print 'neg precision:', nltk.metrics.precision(referenceSets['neg'], testSets['neg'])
        print 'neg recall:', nltk.metrics.recall(referenceSets['neg'], testSets['neg'])
        self.classifier.show_most_informative_features(10)
    
    def train_words(self, feature_select):
        posFeatures = []
        negFeatures = []
        #http://stackoverflow.com/questions/367155/splitting-a-string-into-words-and-punctuation
        #breaks up the sentences into lists of individual words (as selected by the input mechanism) and appends 'pos' or 'neg' after each list
        with open(RT_POLARITY_POS_FILE, 'r') as posSentences:
            for i in posSentences:
                posWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
                posWords = [feature_select(posWords), 'pos']
                posFeatures.append(posWords)
        with open(RT_POLARITY_NEG_FILE, 'r') as negSentences:
            for i in negSentences:
                negWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
                negWords = [feature_select(negWords), 'neg']
                negFeatures.append(negWords)
        trainFeatures = posFeatures[:] + negFeatures[:]
         
        self.classifier = NaiveBayesClassifier.train(trainFeatures)    
   
        test_posFeatures = []
        test_negFeatures = []
        with open(TEST_POLARITY_POS_FILE, 'r') as posSentences:
            for i in posSentences:
                posWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
                posWords = [feature_select(posWords), 'pos']
                test_posFeatures.append(posWords)
        with open(TEST_POLARITY_NEG_FILE, 'r') as negSentences:
            for i in negSentences:
                negWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
                negWords = [feature_select(negWords), 'neg']
                test_negFeatures.append(negWords)
   
        self.test_trained( test_posFeatures[:] + test_negFeatures[:] )
    
    
    #creates a feature selection mechanism that uses all words
    def make_full_dict(self, words):
        return dict([(word, True) for word in words])
    
    #scores words based on chi-squared test to show information gain (http://streamhacker.com/2010/06/16/text-classification-sentiment-analysis-eliminate-low-information-features/)
    def create_word_scores(self):
        #creates lists of all positive and negative words
        posWords = []
        negWords = []
        with open(RT_POLARITY_POS_FILE, 'r') as posSentences:
            for i in posSentences:
                posWord = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
                posWords.append(posWord)
        with open(RT_POLARITY_NEG_FILE, 'r') as negSentences:
            for i in negSentences:
                negWord = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
                negWords.append(negWord)
        posWords = list(itertools.chain(*posWords))
        negWords = list(itertools.chain(*negWords))
    
        #build frequency distibution of all words and then frequency distributions of words within positive and negative labels
        word_fd = FreqDist()
        cond_word_fd = ConditionalFreqDist()
        for word in posWords:
            word_fd[ word.lower() ] += 1
            cond_word_fd['pos'][ word.lower() ] += 1
    
        for word in negWords:
            word_fd[ word.lower() ] += 1
            cond_word_fd['neg'][ word.lower() ] += 1
    
        #finds the number of positive and negative words, as well as the total number of words
        pos_word_count = cond_word_fd['pos'].N()
        neg_word_count = cond_word_fd['neg'].N()
        total_word_count = pos_word_count + neg_word_count
    
        #builds dictionary of word scores based on chi-squared test
        word_scores = {}
        for word, freq in word_fd.iteritems():
            pos_score = BigramAssocMeasures.chi_sq(cond_word_fd['pos'][word], (freq, pos_word_count), total_word_count)
            neg_score = BigramAssocMeasures.chi_sq(cond_word_fd['neg'][word], (freq, neg_word_count), total_word_count)
            word_scores[word] = pos_score + neg_score
    
        return word_scores
    
    #finds the best 'number' words based on word scores
    def find_best_words(self, word_scores, number):
        best_vals = sorted(word_scores.iteritems(), key=lambda (w, s): s, reverse=True)[:number]
        best_words = set([w for w, s in best_vals])
        return best_words
    
    #creates feature selection mechanism that only uses best words
    def best_word_features(self, words):
        return dict([(word, True) for word in words if word in best_words])
    
    
    def is_sentence_neg_pos(self, sentence):
        sentence_dict = self.make_full_dict( sentence )    
        #puts correctly labeled sentences in referenceSets and the predictively labeled version in testsets
        result = self.classifier.classify( sentence_dict )
    
        return result
   
 
    
