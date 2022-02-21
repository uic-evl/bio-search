""" Flask back-end to query the Lucene indexes from a web front-end """
from os import getenv
from flask import Flask, request
from json import dumps
import lucene

from retrieval.index_reader import Reader
from retrieval.search_results import SearchResultEncoder

app = Flask(__name__)
INDEXDIR = getenv('INDEX_PATH')
lucene.initVM(vmargs=['-Djava.awt.headless=true'])


@app.route('/hello')
def hello():
    """ just to check if server is up """
    return "Hello world!"


@app.route('/search/', methods=['GET'])
def search():
    """ retrieve documents based on query strings """
    # parse query strings
    args = request.args
    term = args['q'] if 'q' in args else None
    start_date = args['from'] if 'from' in args else None
    end_date = args['to'] if 'to' in args else None
    max_docs = args['max_docs'] if 'max_docs' in args else 20
    if 'modalities' in args:
        modalities = args['modalities'].split(' ')
    else:
        modalities = None
    image_only = args['image_only'] if 'image_only' in args else False

    # required at least one filter
    if not term and not start_date and not end_date and not modalities:
        return "query missing "

    reader = Reader(INDEXDIR)
    results = reader.search(terms=term,
                            start_date=start_date,
                            end_date=end_date,
                            modalities=modalities,
                            max_docs=max_docs,
                            only_with_images=image_only)
    encoded = dumps(results, cls=SearchResultEncoder, indent=2)
    return encoded


if __name__ == "__main__":
    app.run()
