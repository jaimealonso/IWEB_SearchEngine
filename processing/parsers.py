import xml.etree.ElementTree as ET
import codecs
import os
from itertools import izip


def cf_xml_parser(corpus_dir, doclist):
    documents = {}
    for filename in doclist:
        path = os.path.join(corpus_dir, filename)
        tree = ET.parse(path)
        root = tree.getroot()
        for child in root:
            document = []
            document_len = 0

            title = child.find('TITLE').text.strip()
            abstract = child.find('ABSTRACT')
            extract = child.find('EXTRACT')
            recordnum = child.find('RECORDNUM').text.strip()

            majorsubj = child.find('MAJORSUBJ')

            if majorsubj is not None:
                majorsubj_aux = majorsubj.findall('TOPIC')
                majorsubj_text = ' '.join([x.text for x in majorsubj_aux if ':' not in x.text] +
                                          [x.text[:x.text.find(':')] for x in majorsubj_aux if ':' in x.text]) + ' '
            else:
                majorsubj_text = ''

            minorsubj = child.find('MINORSUBJ')

            if minorsubj is not None:
                minorsubj_aux = minorsubj.findall('TOPIC')
                minorsubj_text = ' '.join([x.text for x in minorsubj_aux if ':' not in x.text] +
                                          [x.text[:x.text.find(':')] for x in minorsubj_aux if ':' in x.text]) + ' '
            else:
                minorsubj_text = ''

            if abstract is not None:
                document.append(abstract.text)
                document_len += len(abstract.text.split())
            else:
                document.append('')
            if extract is not None:
                document.append(extract.text)
                document_len += len(extract.text.split())
            else:
                document.append('')
            if title is not None:
                document.append(title)
                document_len += len(title.split())
            else:
                document.append('')
            if minorsubj_text is not None:
                document.append(minorsubj_text)
                document_len += len(minorsubj_text.split())
            else:
                document.append('')
            if majorsubj_text is not None:
                document.append(majorsubj_text)
                document_len += len(majorsubj_text.split())
            else:
                document.append('')

            documents[recordnum] = {'text': document, 'len': document_len}

    return documents


def moocs_parser(corpus_dir, dummydoclist):
    text_file = os.path.join(corpus_dir, 'moocs.dat')
    title_file = os.path.join(corpus_dir, 'moocs.dat.names')

    text_f = codecs.open(text_file, 'r', encoding='utf-8')
    title_f = codecs.open(title_file, 'r', encoding='utf-8')

    documents = {}
    docnum = 0

    for text, title in izip(text_f, title_f):
        document = [text, title]
        documents[str(docnum)] = {'text': document}
        docnum += 1

    text_f.close()
    title_f.close()

    return documents


def plain_text_parser(corpus_dir, doclist):
    documents = {}

    for filename in doclist:
        path = os.path.join(corpus_dir, filename)

        with codecs.open(path, encoding='utf-8') as myfile:
            document = myfile.read().replace('\n', '')

        documents[filename] = {'text': [document], 'len': len(document)}

    return documents