import operator
from collections import defaultdict
from processing.preprocessor import preprocess


def index_conversion(index):
    d = defaultdict(list)

    for word, priority in index:
        d[word].append(priority)
    terms = dict((k, v) for (k, v) in d.items())

    simple_index = {}
    for word in terms:
        simple_index[word] = {}
        for priority in terms[word]:
            for document in index[(word, priority)]:
                if document in simple_index[word]:
                    simple_index[word][document][0] += index[(word, priority)][document][0]
                else:
                    simple_index[word][document] = [index[(word, priority)][document][0],
                                                    index[(word, priority)][document][1]]

    return simple_index


def search(query, index, doclist):
    index_aux = index[0]
    simple_index = index_conversion(index_aux)

    words = preprocess(query, None)

    query_freqs = {q: words.count(q) for q in words}
    relevance_list = {}

    for doc in doclist:
        value = 0
        for term in query_freqs:
            # if term in index_aux:
            if term in simple_index:
                if doc in simple_index[term]:
                    value += query_freqs[term]*simple_index[term][doc][0]*simple_index[term][doc][1]
        if value > 0:
            relevance_list[doc] = value

    sorted_list = sorted(relevance_list.items(), key=operator.itemgetter(1), reverse=True)

    return sorted_list[:100]