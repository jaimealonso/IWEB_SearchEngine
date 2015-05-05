from __future__ import absolute_import
import xml.etree.ElementTree as ET
from reference.search import search as ref_search
from improved.search import search as imp_search
from processing import parsers, indexer
import matplotlib.pyplot as plt
import numpy
import os
import time


class QueryResults:

    def __init__(self, rec, prec, query_number, pa10=0, r_precision=0, elapsed_time=0, total_rec=0, total_prec=0):
        self.rec = rec
        self.prec = prec
        self.query_number = query_number
        self.pa10 = pa10
        self.r_precision = r_precision
        self.elapsed_time = elapsed_time
        self.total_rec = total_rec
        self.total_prec = total_prec

    @staticmethod
    def get_normalized_rec():
        return [i/10.0 for i in range(0, 11)]

    def get_f_measure(self):
        if self.total_rec == 0 and self.total_prec == 0:
            return 0.0
        else:
            return (2*self.total_prec*self.total_rec)/(self.total_prec+self.total_rec)

    def get_normalized_prec(self):
        normalized_prec = []
        for (indice1, t) in enumerate(self.get_normalized_rec()):
            if t in self.rec:
                normalized_prec.append(self.prec[self.rec.index(t)])
            else:
                rec_aux = [x for x in self.rec if x > t]

                if len(rec_aux) > 0:
                    indice = self.rec.index(min(rec_aux, key=lambda y: abs(y-t)))
                else:
                    indice = len(self.rec) - 1

                normalized_prec.append(self.prec[indice])

        return normalized_prec

    def get_map(self):
        if len(self.rec) > 0:
            normalized_prec = self.get_normalized_prec()[1:]
            maprec = sum(normalized_prec)/10
            return maprec
        else:
            return 0

    def __str__(self):
        value_ref = str(self.query_number) + ',' + str(self.elapsed_time) + ',' + str(self.total_prec) + ',' + str(self.total_rec) + ',' + \
                    str(self.get_f_measure()) + ',' + str(self.pa10) + ',' + str(self.get_map()) + ',' + str(self.r_precision)
        return value_ref


# extracted from http://stackoverflow.com/a/14940026
def sum_digits(n):
    s = 0
    while n:
        s += n % 10
        n /= 10
    return s


def cf_queries_parser(queries_path):
    queries = {}
    tree = ET.parse(os.path.join(queries_path, 'cfquery.xml'))
    root = tree.getroot()
    for child in root:
        querynum = child.find('QueryNumber').text
        querytext = ' '.join(child.find('QueryText').text.replace('\n', '').split())
        records = child.find('Records').findall('Item')

        queries[querynum] = {"text": querytext}
        queries[querynum]['results'] = []

        for item in records:
            score = sum_digits(int(item.attrib['score']))
            if score > 1:
                queries[querynum]['results'].append(item.text)

    return queries


def moocs_queries_parser(queries_path):
    queries = {}
    query_text_f = open(os.path.join(queries_path, 'moocs-queries.txt'))
    query_result_f = open(os.path.join(queries_path, 'moocs-qrels.txt'))

    querynum = 0
    for query in query_text_f:
        queries[str(querynum)] = {'text': query, 'results': []}
        querynum += 1
    query_text_f.close()

    for result in query_result_f:
        fields = result.strip().split()
        queries[fields[0]]['results'].append(fields[1])
    query_result_f.close()

    return queries


def tester(queries_function, queries_path, index, doclist, search_function):

    queries = queries_function(queries_path)
    query_result_array = []

    for (j, query) in enumerate(queries):
        start = time.time()
        result_set = search_function(queries[query]['text'], index, doclist)
        end = time.time()
        elapsed_time = end - start
        actual_results = [num.strip("0") for (num, relevance) in result_set]
        expected_results = queries[query]['results']

        precision = []
        recall = []
        prec = []
        rec = []

        pa10_value = 0
        r_prec_value = 0
        for (i, res) in enumerate(actual_results):
            if len(precision) > 0:
                previous_value_p = precision[len(precision)-1]
                previous_value_r = recall[len(recall)-1]
            else:
                previous_value_p = 0.0
                previous_value_r = 0.0
            if res in expected_results:

                prec_value = previous_value_p + 1.0
                precision.append(prec_value)

                prec.append(prec_value/(i+1.0))
                rec_value = previous_value_r + 1.0
                recall.append(rec_value)
                rec.append(rec_value/len(expected_results))
            if i == 9:
                if len(prec) == 0:
                    pa10_value = 0
                else:
                    pa10_value = prec[-1:][0]

            if len(actual_results) >= len(expected_results):
                if i == (len(expected_results) - 1):
                    if len(prec) == 0:
                        r_prec_value = 0
                    else:
                        r_prec_value = prec[-1:][0]
            elif i == (len(actual_results) - 1):
                r_prec_value = 0

        if len(rec) > 0:
            if rec[len(rec) - 1] < 1.0:
                next_whole_value = (((rec[len(rec) - 1]*10//1) + 1)/10.0)

                while next_whole_value <= 1.0:
                    rec.append(next_whole_value)
                    prec.append(0.0)
                    next_whole_value += 0.1

            if rec[0] > 0.0:
                rec = [0.0] + rec
                prec = [prec[0]] + prec

        coincidences = list(set(actual_results).intersection(expected_results))

        if len(actual_results) > 0:
            total_prec = float(len(coincidences))/len(actual_results)
        else:
            total_prec = 0

        total_rec = float(len(coincidences))/len(expected_results)

        query_result_array.append(QueryResults(rec, prec, j, pa10_value, r_prec_value, elapsed_time, total_rec, total_prec))

    return query_result_array


def plot_figures(plot_title, query_results_ref, query_results_imp, result_file):
        fig = plt.figure(figsize=(8, 6))

        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(plot_title)
        plt.ylim(-0.1, 1.1)
        plt.xlim(0.0, 1.0)
        plt.locator_params(axis='x', nbins='11')
        if len(query_results_ref.rec) > 0:
            plt.plot(query_results_ref.get_normalized_rec(), query_results_ref.get_normalized_prec(), 'o-', color='red')
        if len(query_results_imp.rec) > 0:
            plt.plot(query_results_imp.get_normalized_rec(), query_results_imp.get_normalized_prec(), 'o-', color='green')

        fig.savefig(result_file)
        fig.show()


def general_analysis(query_array_ref, query_array_imp, result_file_path):
    # printing analysis results in CSV format
    ref_csv_file = 'results_reference.csv'
    imp_csv_file = 'results_improved.csv'

    ref_file = open(os.path.join(result_file_path, ref_csv_file), 'w')
    imp_file = open(os.path.join(result_file_path, imp_csv_file), 'w')
    ref_file.write('query#,time,prec,rec,f_measure,p@10,map,r_precision\n')
    imp_file.write('query#,time,prec,rec,f_measure,p@10,map,r_precision\n')
    prec_array_ref = []
    prec_array_imp = []
    for (indice, i) in enumerate(query_array_ref):

        ref_file.write(str(i)+'\n')
        imp_file.write(str(query_array_imp[indice])+'\n')

        if len(i.rec) > 0:
            prec_array_ref.append(i.get_normalized_prec())
        if len(query_array_imp[indice].rec) > 0:
            prec_array_imp.append(query_array_imp[indice].get_normalized_prec())

    normalized_rec = QueryResults.get_normalized_rec()
    prec_ref_avg = numpy.array(numpy.average(numpy.matrix(prec_array_ref), axis=0))[0].tolist()
    prec_imp_avg = numpy.array(numpy.average(numpy.matrix(prec_array_imp), axis=0))[0].tolist()

    query_ref_avg = QueryResults(normalized_rec, prec_ref_avg, 0)
    query_imp_avg = QueryResults(normalized_rec, prec_imp_avg, 0)

    plot_title = 'Average Precision vs Recall'
    plot_figures(plot_title, query_ref_avg, query_imp_avg, os.path.join(result_file_path, 'avg_p_vs_r_graph.png'))

    ref_file.close()
    imp_file.close()


def main_test(queries_path, index_path, corpus_dir, results_dir, corpus_type):

    print 'Testing...'

    if corpus_type == 'cf':
        parser_function = parsers.cf_xml_parser
        queries_function = cf_queries_parser
    else:
        parser_function = parsers.moocs_parser
        queries_function = moocs_queries_parser

    index = indexer.get_index(corpus_dir, parser_function, index_path)
    doclist = index[1].keys()

    query_array_ref = tester(queries_function, queries_path, index, doclist, ref_search)
    query_array_imp = tester(queries_function, queries_path, index, doclist, imp_search)
    general_analysis(query_array_ref, query_array_imp, results_dir)
