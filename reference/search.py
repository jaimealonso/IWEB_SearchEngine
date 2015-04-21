import nltk
import operator


def search(query, index, doclist):
    words = query.split()
    stemmer = nltk.stem.porter.PorterStemmer()
    query_freqs = {stemmer.stem(q): words.count(q) for q in words}
    relevance_list = {}

    for doc in doclist:
        value = 0
        for term in query_freqs:
            if term in index:
                if doc in index[term]:
                    value += query_freqs[term]*index[term][doc]
        if value > 0:
            relevance_list[doc] = value

    sorted_list = sorted(relevance_list.items(), key=operator.itemgetter(1), reverse=True)

    return sorted_list