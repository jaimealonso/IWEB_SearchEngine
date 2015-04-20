import os
import codecs

from preprocessor import preprocess
from math import log10


def indexer(corpus_dir):
    index = {}
    doclist = os.listdir(corpus_dir)
    M = len(doclist)
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
        enhanced_index[word]={} #inner dict
        idf = log10((M+1) / len(index[word])) 
        for document in index[word]:
            enhanced_index[word][document] = index[word][document]*idf

    return enhanced_index


# corpus_dir = 'C:\\Users\\Santi\\git\\IWEB_SearchEngine\\corpus\\'
# index = indexer(corpus_dir)
#
#
#
# print index

