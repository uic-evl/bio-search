""" Flask API for the search interface """

from os import getenv
from flask import Flask, request
from flask_cors import CORS, cross_origin
from markupsafe import escape
from biosearch_core.db.model import ConnectionParams
from biosearch_core.controllers.search_controller import SearchController
from biosearch_core.controllers.lucene_controller import LuceneController

# initialize Flask
app = Flask(__name__)
CORS(app)

# environmental variables
INDEXDIR = getenv("INDEX_PATH")
CORD19_INDEX_DIR = getenv("CORD_INDEX_PATH")
# DATADIR = getenv("DATA_PATH")
# BBOXESDIR = getenv("BBOXES_PATH")
ROOT = getenv("FLASK_ROOT")
SCHEMA = getenv("SCHEMA")


conn_params = ConnectionParams(
    host=getenv("host"),
    port=getenv("port"),
    dbname=getenv("dbname"),
    user=getenv("user"),
    password=getenv("password"),
    schema=SCHEMA,
)


@cross_origin()
@app.route(ROOT + "/hello")
def hello():
    """just to check if server is up"""
    return "Hello world!"


@cross_origin
@app.route(ROOT + "/document/<doc_id>", methods=["GET"])
def get_document_db(doc_id: int):
    """test function"""
    document_id = int(escape(doc_id))
    controller = SearchController(conn_params)
    document = controller.fetch_surrogate_data(document_id)
    return document


@cross_origin()
@app.route(ROOT + "/search/", methods=["GET"])
def search():
    """retrieve documents based on query strings"""
    args = request.args
    dataset = args["ds"]
    if dataset is None:
        raise ValueError("parameter dataset cannot be null")
    if dataset not in ["gxd", "cord19"]:
        raise ValueError(f"parameter dataset {dataset} is invalid")
    terms = args["q"] if "q" in args else None
    full_text = True if args["ft"] == "true" else False
    start_date = args["from"] if "from" in args else None
    end_date = args["to"] if "to" in args else None
    max_docs = int(args["max_docs"]) if "max_docs" in args else 20
    modalities = args["modalities"] if "modalities" in args else None

    index_dir = INDEXDIR if dataset == "gxd" else CORD19_INDEX_DIR
    controller = LuceneController(index_dir)
    return controller.search(
        terms, start_date, end_date, max_docs, modalities, full_text
    )


@cross_origin
@app.route(ROOT + "/taxonomy/<string:taxonomy>", methods=["GET"])
def fetch_taxonomy(taxonomy):
    """TODO: do i need this?"""
    taxonomy = escape(taxonomy)
    return {}
