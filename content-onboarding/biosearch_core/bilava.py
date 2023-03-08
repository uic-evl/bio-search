""" Flask API for the search interface """

from os import getenv
from flask import Flask
from flask_cors import CORS, cross_origin
from markupsafe import escape
from biosearch_core.db.model import ConnectionParams
from biosearch_core.controllers import bilava

# initialize Flask
app = Flask(__name__)
CORS(app)

# environmental variables
ROOT = getenv("FLASK_ROOT")


@cross_origin
@app.route(ROOT + "/tree/<string:project>", methods=["GET"])
def fetch_taxonomy(project):
    """Retrieve labels from db"""
    project = escape(project)
    conn_params = ConnectionParams(
        host=getenv("host"),
        port=getenv("port"),
        dbname=getenv("dbname"),
        user=getenv("user"),
        password=getenv("password"),
        schema=project,
    )
    return bilava.fetch_labels_list(conn_params)
