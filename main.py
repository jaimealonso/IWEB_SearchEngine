import argparse
from improved import search as imp_search
from reference import search as ref_search
from processing import parsers, indexer
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='IWEB Search Engine')

    parser.add_argument('-r', dest='engine', action='store_const', const='reference', default='improved',
                        help='uses the reference search engine')
    parser.add_argument('-i', dest='engine', action='store_const', const='improved', default='improved',
                        help='uses the improved search engine')
    parser.add_argument('--index', dest='index_path', default='resources/index.dat',
                        help='specifies the path to the index file')
    parser.add_argument('--corpus_dir', dest='corpus_dir', default='resources/corpus/',
                        help='specifies the path to the corpus directory')
    parser.add_argument('--cf', dest='corpus_type', action='store_const', const='cf', default='cf',
                        help='parses corpus using the Cystic Fibrosis Database model')
    parser.add_argument('--plain', dest='corpus_type', action='store_const', const='plain', default='cf',
                        help='parses corpus as plain text')
    parser.add_argument('--build-index', dest='build_index', action='store_const', const=True, default=False,
                        help='forces program to rebuild the index')

    args = parser.parse_args()

    if args.engine == 'reference':
        search_function = ref_search.search
    else:
        search_function = imp_search.search
    if args.corpus_type == 'plain':
        parse_function = parsers.plain_text_parser
    else:
        parse_function = parsers.cf_xml_parser

    if not os.path.isdir(os.path.abspath('resources/')):
        os.mkdir(os.path.abspath('resources/'))

    index_path = os.path.abspath(args.index_path)
    corpus_dir = os.path.abspath(args.corpus_dir)

    query = raw_input('Please insert your query: ')

    if args.build_index:
        os.remove(index_path)

    index = indexer.get_index(corpus_dir, parse_function, index_path)
    doclist = index[1].keys()

    print search_function(query, index, doclist)