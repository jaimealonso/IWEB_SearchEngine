from __future__ import division # this is for float point division
from indexer import indexer

import os.path
import codecs
import cPickle as pickle #this is because is v2.7 and we need cPickle

def indexCorpus(): #this function loads the index or creates it if nonexistant
    index={}
    if not (os.path.isfile('index.dat')):
        corpus_dir = 'C:\\Users\\Santi\\git\\IWEB_SearchEngine\\corpus\\'
        index = indexer(corpus_dir)
        with open ('index.dat','w') as f:
            pickle.dump(index, f, protocol=0)
    else:
      index = open('index.dat', 'r').read()
    return index

print "begin"
indexCorpus()
query = raw_input('Welcome to the Reference Search Engine v0.1\nPlease insert your query:')
index = pickle.load(open('index.dat','r'))

words = query.split()
result = {}
index_keys = index.keys()
for query_word in words:
    freq_word = 1/len(words)
    if query_word in index_keys:
        print "inside index keys"
        inner_dict = index[query_word]
        for w in inner_dict:
           value = freq_word*inner_dict[w]
           print value
           result[w]=value

print result

        
        
        
    
            
        