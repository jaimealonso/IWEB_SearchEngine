import operator
from collections import defaultdict
from numpy import exp
import numpy
from processing.preprocessor import preprocess


def index_conversion(index, doclens, bmin=0.1, bmax=0.8):
    d = defaultdict(list)

    for word, priority in index:
        d[word].append(priority)
    terms = dict((k, v) for (k, v) in d.items())

    num_fields = max([priority for p in terms for priority in terms[p]]) + 1
    if num_fields == 1:
        bc = [bmax]
    else:
        bc = numpy.linspace(bmin, bmax, num=num_fields).tolist()

    simple_index = {}
    for word in terms:
        simple_index[word] = {}
        for priority in terms[word]:
            boost = exp(priority + 2)
            inner_bc = bc[priority]
            for document in index[(word, priority)]:
                field_len = doclens[document][priority]
                avg_field_len = doclens['avg'][priority]
                if document in simple_index[word]:
                    simple_index[word][document][0] += (boost*index[(word, priority)][document][0])/((1-inner_bc)+inner_bc*(field_len/avg_field_len))
                else:
                    simple_index[word][document] = [(boost*index[(word, priority)][document][0])/((1-inner_bc)+inner_bc*(field_len/avg_field_len)),
                                                    index[(word, priority)][document][1]]

    return simple_index


def search(query, index, doclist, k=18.0, b=0.75):
    words = preprocess(query, None)

    query_freqs = {q: words.count(q) for q in words}
    relevance_list = {}
    index_aux = index_conversion(index[0], index[1])

    for doc in doclist:
        value = 0
        for term in query_freqs:

            if term in index_aux:
                if doc in index_aux[term]:
                    num = index_aux[term][doc][0]*index_aux[term][doc][1]
                    den = k + index_aux[term][doc][0]

                    value += num / den
        if value > 0:
            relevance_list[doc] = value

    sorted_list = sorted(relevance_list.items(), key=operator.itemgetter(1), reverse=True)

    return sorted_list[:100]
