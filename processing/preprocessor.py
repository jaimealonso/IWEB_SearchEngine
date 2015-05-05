import nltk
import os


def preprocess(document, stopword_list):

    # tokenize document
    tokens = [token.lower() for token in nltk.word_tokenize(document)]

    # remove punctuation marks and stopwords
    punctuation_marks = ['.', '?', '!', ':', ';', '-', '(', ')', '[', ']', '"', '/', ',']

    if stopword_list is None:
        stopword_file = open(os.path.join(os.path.dirname(__file__), 'stopword_list.txt'), 'r')
        stopword_list = []

        for line in stopword_file:
            stopword_list.append(line.rstrip())

    stemmer = nltk.stem.porter.PorterStemmer()
    tokens = [stemmer.stem(token) for token in tokens if token not in stopword_list + punctuation_marks]

    return tokens


