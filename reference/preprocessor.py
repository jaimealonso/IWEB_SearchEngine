import nltk


def preprocess(document):

    # tokenize document
    tokens = [token.lower() for token in nltk.word_tokenize(document)]

    # remove punctuation marks and stopwords
    punctuation_marks = ['.', '?', '!', ':', ';', '-', '(', ')', '[', ']', '"', '/', ',']

    stopword_file = open('../stopword_list.txt', 'r')
    stopword_list = []

    for line in stopword_file:
        stopword_list.append(line.rstrip())

    stemmer = nltk.stem.porter.PorterStemmer()
    tokens = [stemmer.stem(token) for token in tokens if token not in stopword_list + punctuation_marks]

    return tokens



sentence = "Hey y'all, this is a sample sentence that I want to tokenize; sorry, I am going to use a lot of punctuation " \
           "marks."
x = preprocess(sentence)

