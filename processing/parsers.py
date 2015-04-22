import xml.etree.ElementTree as ET
import codecs
import os


def cf_xml_parser(corpus_dir, doclist):
    documents = {}
    for filename in doclist:
        path = os.path.join(corpus_dir, filename)
        tree = ET.parse(path)
        root = tree.getroot()
        for child in root:
            document = ""

            title = child.find('TITLE')
            abstract = child.find('ABSTRACT')
            extract = child.find('EXTRACT')
            recordnum = child.find('RECORDNUM').text.strip()
            if title is not None:
                document += title.text
            if abstract is not None:
                document += " " + abstract.text
            if extract is not None:
                document += " " + extract.text

            documents[recordnum] = document

    return documents


def plain_text_parser(corpus_dir, doclist):
    documents = {}

    for filename in doclist:
        path = os.path.join(corpus_dir, filename)

        with codecs.open(path, encoding='utf-8') as myfile:
            document = myfile.read().replace('\n', '')

        documents[filename] = document

    return documents