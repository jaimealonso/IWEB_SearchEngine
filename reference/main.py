from indexer import get_index, indexer
from search import search
import os


if __name__ == "__main__":
    corpus_dir = "/Users/jaime/PycharmProjects/IWEB_SearchEngine/Cystic Fibrosis Database/"
    query = raw_input('Welcome to the Reference Search Engine v0.2\nPlease insert your query:')
    index = get_index(corpus_dir, indexer)
    doclist = os.listdir(corpus_dir)

    print search(query, index, doclist)