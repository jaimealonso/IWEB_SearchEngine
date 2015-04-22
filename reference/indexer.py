import os
import codecs
import cPickle as pickle

from preprocessor import preprocess
from math import log10


def get_index(corpus_dir, index_function):  # this function loads the index or creates it if nonexistant
    if not (os.path.isfile('index.dat')):
        index = index_function(corpus_dir)
        with open('index.dat', 'w') as f:
            pickle.dump(index, f, protocol=0)
    else:
        index = pickle.load(open('index.dat', 'r'))
    return index


def indexer(corpus_dir):
    index = {}
    doclist = os.listdir(corpus_dir)
    m = len(doclist)
    # extract tokens from files
    for filename in doclist:

        with codecs.open(corpus_dir+filename, encoding='utf-8') as myfile:
            document = myfile.read().replace('\n', '')

        tokens = preprocess(document)

        for token in tokens:
            if token in index:
                if filename in index[token]:
                    index[token][filename] += 1
                else:
                    index[token][filename] = 1
            else:
                index[token] = {filename: 1}

    enhanced_index = {}
    for word in index:
        enhanced_index[word] = {}  # inner dict
        idf = log10((m+1.0) / len(index[word]))
        for document in index[word]:
            enhanced_index[word][document] = index[word][document]*idf

    return enhanced_index

