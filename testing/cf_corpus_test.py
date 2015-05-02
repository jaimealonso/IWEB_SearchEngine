from __future__ import absolute_import
import xml.etree.ElementTree as ET
from reference.search import search as ref_search
from improved.search import search as imp_search
from processing import parsers, indexer
from matplotlib.pylab import plot
import matplotlib.pyplot as plt
import numpy


class QueryResults:

    def __init__(self, rec, prec, query_number, total_rec=0, total_prec=0):
        self.rec = rec
        self.prec = prec
        self.query_number = query_number
        self.total_rec = total_rec
        self.total_prec = total_prec

    def get_normalized_rec(self):
        return [i/10.0 for i in range(0, 11)]

    def get_f_measure(self):
        if self.total_rec == 0 and self.total_prec == 0:
            return 0.0
        else:
            return (2*self.total_prec*self.total_rec)/(self.total_prec+self.total_rec)

    def get_normalized_prec(self):
        normalized_prec = []
        for (indice1, t) in enumerate(self.get_normalized_rec()):
            # print t
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


# extracted from http://stackoverflow.com/a/14940026
def sum_digits(n):
    s = 0
    while n:
        s += n % 10
        n /= 10
    return s


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
            score = sum_digits(int(item.attrib['score']))
            if score > 1:
                queries[querynum]['results'].append(item.text)

    return queries


def cf_tester(queries_path, index, doclist, search_function):
    queries = cf_queries_parser(queries_path)

    query_result_array = []
    print len(queries)

    for (j, query) in enumerate(queries):
        print "Query number: " + str(j)
        result_set = search_function(queries[query]['text'], index, doclist)
        actual_results = [num.strip("0") for (num, relevance) in result_set]
        expected_results = queries[query]['results']

        precision = []
        recall = []
        prec = []
        rec = []

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
        total_prec = float(len(coincidences))/len(actual_results)
        total_rec = float(len(coincidences))/len(expected_results)

        print str(total_prec) + ", " + str(total_rec)

        query_result_array.append(QueryResults(rec, prec, j, total_rec, total_prec))

    return query_result_array


def plot_figures(query_results_ref, query_results_imp):
        fig = plt.figure(figsize=(8, 6))

        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision vs Recall for Query ' + str(query_results_ref.query_number))
        plt.ylim(-0.1, 1.1)
        plt.xlim(0.0, 1.0)
        plt.locator_params(axis='x', nbins='11')
        plt.plot(query_results_ref.get_normalized_rec(), query_results_ref.get_normalized_prec(), 'o-', color='red')
        plt.plot(query_results_imp.get_normalized_rec(), query_results_imp.get_normalized_prec(), 'o-', color='green')

        # plt.grid(True)

        fig.savefig("img_ref/query"+str(query_results_ref.query_number)+".png")


def general_analysis(query_array_ref, query_array_imp, result_file_path):
    # printing analysis results in CSV format
    f = open(result_file_path, 'w')
    f.write('query#,prec_ref,rec_ref,f_ref,prec_imp,rec_imp,f_imp\n')

    prec_array_ref = []
    prec_array_imp = []
    for (indice, i) in enumerate(query_array_ref):
        value = str(i.query_number) + ',' + str(i.total_prec) + ',' + str(i.total_rec) + ',' + \
                str(i.get_f_measure())
        value += ',' + str(query_array_imp[indice].total_prec) + ',' + str(query_array_imp[indice].total_rec) \
                 + ',' + str(query_array_imp[indice].get_f_measure())
        f.write(value+'\n')

        prec_array_ref.append(i.get_normalized_prec())
        prec_array_imp.append(query_array_imp[indice].get_normalized_prec())

    normalized_rec = query_array_ref[0].get_normalized_rec()
    prec_ref_avg = numpy.array(numpy.average(numpy.matrix(prec_array_ref), axis=0))[0].tolist()
    prec_imp_avg = numpy.array(numpy.average(numpy.matrix(prec_array_imp), axis=0))[0].tolist()

    query_ref_avg = QueryResults(normalized_rec, prec_ref_avg, 0)
    query_imp_avg = QueryResults(normalized_rec, prec_imp_avg, 0)

    plot_figures(query_ref_avg, query_imp_avg)

    f.close()


if __name__ == "__main__":
    queries_path = "/Users/jaime/PycharmProjects/IWEB_SearchEngine/Cystic Fibrosis Database/TEST/cfquery.xml"
    index_path = "/Users/jaime/PycharmProjects/IWEB_SearchEngine/resources/index.dat"
    corpus_dir = "/Users/jaime/PycharmProjects/IWEB_SearchEngine/resources/corpus/"
    index = indexer.get_index(corpus_dir, parsers.cf_xml_parser, index_path)
    doclist = index[1].keys()

    query_array_ref = cf_tester(queries_path, index, doclist, ref_search)
    query_array_imp = cf_tester(queries_path, index, doclist, imp_search)

    # general_analysis(query_array_ref, query_array_imp, 'results.csv')

    for (indice, i) in enumerate(query_array_ref):
        plot_figures(i, query_array_imp[indice])