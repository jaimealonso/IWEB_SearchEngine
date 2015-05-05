import argparse
from improved import search as imp_search
from reference import search as ref_search
from processing import parsers, indexer
import os
from testing import corpus_test
import ConfigParser


def generate_config(config, file_path):
    cfgfile = open(file_path, 'w')

    config.add_section('SearchEngineVariables')
    config.set('SearchEngineVariables', 'engine', 'improved')
    config.set('SearchEngineVariables', 'index_path', 'resources/index.dat')
    config.set('SearchEngineVariables', 'corpus_dir', 'resources/corpus/')
    config.set('SearchEngineVariables', 'corpus_type', 'cf')
    config.set('SearchEngineVariables', 'build_index', False)
    config.set('SearchEngineVariables', 'queries_path', 'resources/corpus/test/')
    config.set('SearchEngineVariables', 'results_dir', 'resources/results')
    config.write(cfgfile)
    cfgfile.close()


def parse_config(config, file_path):
    settings_dict = {}
    config.read(file_path)

    parameters = ['engine', 'index_path', 'corpus_dir', 'corpus_type', 'build_index',
                  'queries_path', 'results_dir']

    for p in parameters:
        settings_dict[p] = config.get('SearchEngineVariables', p, 0)

    return settings_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='IWEB Search Engine')

    parser.add_argument('--test', dest='test', action='store_const', const=True, default=False,
                        help='executes test bench')

    args = parser.parse_args()

    config_obj = ConfigParser.ConfigParser()
    settings_file = 'settings.conf'

    if not os.path.exists(settings_file):
        generate_config(config_obj, settings_file)

    settings = parse_config(config_obj, settings_file)

    if settings['engine'] == 'reference':
        search_function = ref_search.search
    else:
        search_function = imp_search.search
    if settings['corpus_type'] == 'plain':
        parse_function = parsers.plain_text_parser
    elif settings['corpus_type'] == 'moocs':
        parse_function = parsers.moocs_parser
    else:
        parse_function = parsers.cf_xml_parser

    if not os.path.isdir(os.path.abspath('resources/')):
        os.mkdir(os.path.abspath('resources/'))
    if not os.path.isdir(os.path.abspath('resources/results/')):
        os.mkdir(os.path.abspath('resources/results/'))

    index_path = os.path.abspath(settings['index_path'])
    corpus_dir = os.path.abspath(settings['corpus_dir'])

    if settings['build_index'] == 'True':
        if os.path.exists(settings['index_path']):
            os.remove(settings['index_path'])

    if args.test:
        corpus_test.main_test(settings['queries_path'], index_path, corpus_dir, settings['results_dir'],
                              settings['corpus_type'])
    else:
        query = raw_input('Please insert your query: ')

        index = indexer.get_index(corpus_dir, parse_function, index_path)
        doclist = index[1].keys()

        print search_function(query, index, doclist)