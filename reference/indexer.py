import os, codecs
from preprocessor import preprocess


def indexer(corpus_dir):
    index = {}

    # extract tokens from files
    for filename in os.listdir(corpus_dir):

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

    return index


corpus_dir = '/Users/jaime/PycharmProjects/IWEB_SearchEngine/corpus/'
index = indexer(corpus_dir)
for key in index:
    print key

