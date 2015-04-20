from __future__ import division # this is for float point division
from indexer import indexer

import os.path
import operator
import cPickle as pickle # this is because is v2.7 and we need cPickle

def indexCorpus(corpus_dir): # this function loads the index or creates it if nonexistant
    index={}
    if not (os.path.isfile('index.dat')):
        index = indexer(corpus_dir)
        with open('index.dat', 'w') as f:
            pickle.dump(index, f, protocol=0)
    else:
      index = open('index.dat', 'r').read()
    return index


corpus_dir = "/Users/jaime/PycharmProjects/IWEB_SearchEngine/corpus/"
print "begin"
indexCorpus(corpus_dir)
query = raw_input('Welcome to the Reference Search Engine v0.1\nPlease insert your query:')
index = pickle.load(open('index.dat', 'r'))

words = query.split()
result = {}
index_keys = index.keys()
query_freqs = {q: words.count(q) for q in words}
print query_freqs
relevance_list = {}
doclist = os.listdir(corpus_dir)

for doc in doclist:
    value = 0
    for term in query_freqs:
        if term in index:
            if doc in index[term]:
                value += query_freqs[term]*index[term][doc]
    if value > 0:
        relevance_list[doc] = value

sorted_list = sorted(relevance_list.items(), key=operator.itemgetter(1), reverse=True)
print sorted_list