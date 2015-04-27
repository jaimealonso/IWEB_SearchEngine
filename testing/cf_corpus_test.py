import xml.etree.ElementTree as ET
from improved.search import search
from processing import parsers, indexer


def cf_queries_parser(queries_path):
    queries = {}
    tree = ET.parse(queries_path)
    root = tree.getroot()
    for child in root:
        querynum = child.find('QueryNumber').text
        querytext = ' '.join(child.find('QueryText').text.replace('\n', '').split())
        records = child.find('Records').findall('Item')

        queries[querynum] = {"text": querytext}
        queries[querynum]['results'] = []

        for item in records:
            queries[querynum]['results'].append(item.text)

    return queries


def cf_tester(queries_path, index, doclist):
    queries = cf_queries_parser(queries_path)

    for query in queries:
        result_set = search(queries[query]['text'], index, doclist)
        actual_results = [num.strip("0") for (num, relevance) in result_set]
        expected_results = queries[query]['results']

        coincidences = list(set(actual_results).intersection(expected_results))
        print coincidences
        precision = float(len(coincidences))/len(actual_results)
        recall = float(len(coincidences))/len(expected_results)
        f_measure = (2*precision*recall)/(precision+recall)

        print "Precision: " + str(precision) + " Recall: " + str(recall) + " F1-measure: " + str(f_measure)


if __name__ == "__main__":
    queries_path = "/Users/jaime/PycharmProjects/IWEB_SearchEngine/Cystic Fibrosis Database/TEST/cfquery.xml"
    index_path = "/Users/jaime/PycharmProjects/IWEB_SearchEngine/resources/index.dat"
    corpus_dir = "/Users/jaime/PycharmProjects/IWEB_SearchEngine/resources/corpus/"
    index = indexer.get_index(corpus_dir, parsers.cf_xml_parser, index_path)
    doclist = index[1].keys()

    cf_tester(queries_path, index, doclist)