from preprocessor import preprocess
from math import log10
import cPickle as pickle
import os


def get_index(corpus_dir, parser_function, index_path):  # this function loads the index or creates it if nonexistant
    # resources_dir = os.path.dirname(os.path.dirname(__file__)) + "/resources/"
    if not (os.path.isfile(index_path)):
        doclist = [docname for docname in os.listdir(corpus_dir) if docname != '.DS_Store']
        documents = parser_function(corpus_dir, doclist)
        index = improved_indexer(documents)
        with open(index_path, 'w') as f:
            pickle.dump(index, f, protocol=0)
    else:
        index = pickle.load(open(index_path, 'r'))
    return index


def improved_indexer(documents):
    index = {}
    m = len(documents)
    doc_lengths = {}

    for recordnum in documents:
        document = documents[recordnum]

        tokens = preprocess(document)
        for token in tokens:
            if token in index:
                if recordnum in index[token]:
                    index[token][recordnum] += 1
                else:
                    index[token][recordnum] = 1
            else:
                index[token] = {recordnum: 1}

        doc_lengths[recordnum] = len(tokens)

    doc_lengths['avg'] = sum(doc_lengths.itervalues())/m

    enhanced_index = {}
    for word in index:
        enhanced_index[word] = {}  # inner dict
        idf = log10((m+1.0) / len(index[word]))
        for document in index[word]:
            enhanced_index[word][document] = [index[word][document], idf]

    return [enhanced_index, doc_lengths]