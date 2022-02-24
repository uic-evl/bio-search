""" Flask back-end to query the Lucene indexes from a web front-end """
from os import getenv
from json import dumps, load
from flask import Flask, request
from flask_cors import CORS, cross_origin
from markupsafe import escape
import lucene

from .retrieval.index_reader import Reader
from .retrieval.search_results import SearchResultEncoder

app = Flask(__name__)
CORS(app)
INDEXDIR = getenv('INDEX_PATH')
DATADIR = getenv('DATA_PATH')
PDFSDIR = getenv('PDFS_PATH')

GXD_DATA = None
with open(DATADIR, 'r') as f:
  GXD_DATA = load(f)

@cross_origin()
@app.route('/hello')
def hello():
    """ just to check if server is up """
    return "Hello world!"

@cross_origin()
@app.route('/search/', methods=['GET'])
def search():
    """ retrieve documents based on query strings """
    vm_env = lucene.getVMEnv() or lucene.initVM(  # pylint: disable=no-member
        vmargs=['-Djava.awt.headless=true'])
    vm_env.attachCurrentThread()

    # parse query strings
    args = request.args
    print(args)
    term = args['q'] if 'q' in args else None
    start_date = args['from'] if 'from' in args else None
    end_date = args['to'] if 'to' in args else None
    max_docs = int(args['max_docs']) if 'max_docs' in args else 20
    if 'modalities' in args:
        modalities = args['modalities'].split(' ')
    else:
        modalities = None
    image_only = args['image_only'] if 'image_only' in args else False
    highlight = True if 'highlight' in args else False

    # required at least one filter
    if not term and not start_date and not end_date and not modalities:
        return "query missing "

    reader = Reader(INDEXDIR)
    results = reader.search(terms=term,
                            start_date=start_date,
                            end_date=end_date,
                            modalities=modalities,
                            max_docs=max_docs,
                            only_with_images=image_only,
                            highlight=highlight)

    for result in results:
        result.modalities_count = GXD_DATA[result.id]['modalities']

    encoded = dumps(results, cls=SearchResultEncoder, indent=2)
    return encoded


@cross_origin
@app.route('/document/<id>', methods=['GET'])
def get_document(id):
    document_id = escape(id)
    document = GXD_DATA[document_id].copy()
    document['pages'] = [ {"page": page, "figures": figures} for (page, figures) in document['pages'].items()]
    for page in document['pages']:
        page['page_url'] = f"{document_id}/{document_id}-{str(page['figures'][0]['page']).zfill(6)}.png"

    document['first_page'] = f"{document_id}/{document_id}-000001.png"
    return document



if __name__ == "__main__":
    app.run()
