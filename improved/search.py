import nltk
import operator


def search(query, index, doclist, k=1.2, b=2.0):
    words = query.split()
    stemmer = nltk.stem.porter.PorterStemmer()
    query_freqs = {stemmer.stem(q): words.count(q) for q in words}
    relevance_list = {}

    avg_len = index[1]['avg']

    for doc in doclist:
        value = 0
        doc_len = index[1][doc]
        for term in query_freqs:
            if term in index[0]:
                if doc in index[0][term]:
                    num = query_freqs[term]*index[0][term][doc][0]*index[0][term][doc][1]*(k+1)
                    den = index[0][term][doc][0]+k*(1-b+b*(doc_len/avg_len))
                    value += num / den
        if value > 0:
            relevance_list[doc] = value

    sorted_list = sorted(relevance_list.items(), key=operator.itemgetter(1), reverse=True)

    return sorted_list