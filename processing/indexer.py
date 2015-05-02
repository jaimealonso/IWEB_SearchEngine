from preprocessor import preprocess
from math import log10
from collections import defaultdict
from numpy import exp
import numpy
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
        document = documents[recordnum]['text']
        doc_lengths[recordnum] = []

        for (i, field) in enumerate(document):
            # priority = (i + 1)*10
            # priority = exp(i + 2)
            priority = i
            tokens = preprocess(field)
            for token in tokens:
                if (token, priority) in index:
                    if recordnum in index[(token, priority)]:
                        index[(token, priority)][recordnum] += 1
                    else:
                        index[(token, priority)][recordnum] = 1
                else:
                    index[(token, priority)] = {recordnum: 1}

            doc_lengths[recordnum].append(len(tokens))

    all_doc_lengths = [doc_lengths[recordnum] for recordnum in doc_lengths]
    doc_lengths_avg = numpy.average(numpy.matrix(all_doc_lengths), axis=0).tolist()[0]


    doc_lengths['avg'] = doc_lengths_avg

    enhanced_index = {}
    d = defaultdict(list)

    for word, priority in index:
        d[word].append(priority)
    terms = dict((k, v) for (k, v) in d.items())

    for word in terms:

        docs_with_word_aux = [index[k, v] for k in terms for v in terms[k] if k == word]
        docs_with_word = list(set([item for element in docs_with_word_aux for item in element]))
        idf = log10((m+1.0) / len(docs_with_word))

        for priority in terms[word]:
            enhanced_index[(word, priority)] = {}

            for document in index[(word, priority)]:
                enhanced_index[(word, priority)][document] = [index[(word, priority)][document], idf]


    return [enhanced_index, doc_lengths]