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
ROOT = getenv("FLASK_ROOT")
SCHEMA = getenv("SCHEMA")


conn_params = ConnectionParams(
    host=getenv("DBHOST"),
    port=getenv("DBPORT"),
    dbname=getenv("DBNAME"),
    user=getenv("DBUSER"),
    password=getenv("DBPASSWORD"),
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

    terms = args["q"] if "q" in args else None
    full_text = True if args["ft"] == "true" else False
    start_date = args["from"] if "from" in args else None
    end_date = args["to"] if "to" in args else None
    max_docs = int(args["max_docs"]) if "max_docs" in args else 20
    modalities = args["modalities"] if "modalities" in args else None
    highlight_captions = True if "hc" in args and args["hc"] == "true" else False

    controller = LuceneController(INDEXDIR)
    return controller.search(
        terms,
        start_date,
        end_date,
        max_docs,
        modalities,
        full_text,
        highlight_captions,
    )


@cross_origin
@app.route(ROOT + "/taxonomy/<string:taxonomy>", methods=["GET"])
def fetch_taxonomy(taxonomy):
    """TODO: do i need this?"""
    taxonomy = escape(taxonomy)
    return {}


if __name__ == "__main__":
    app.run(host="0.0.0.0")
