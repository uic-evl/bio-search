""" Flask API for the search interface """

from os import environ, getcwd
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS, cross_origin
from markupsafe import escape
from biosearch_core.db.model import ConnectionParams
from biosearch_core.controllers import bilava

# initialize Flask
load_dotenv(".env")
app = Flask(__name__)
CORS(app)

# environmental variables
ROOT = environ.get("FLASK_ROOT")
PROJECTS_DIR = environ.get("PROJECTS_DIR")
print(PROJECTS_DIR)
print(ROOT)


@cross_origin
@app.route(ROOT + "/tree/<string:project>", methods=["GET"])
def fetch_taxonomy(project):
    """Retrieve labels from db"""
    project = escape(project)
    conn_params = ConnectionParams(
        host=environ.get("host"),
        port=environ.get("port"),
        dbname=environ.get("dbname"),
        user=environ.get("user"),
        password=environ.get("password"),
        schema=project,
    )
    return bilava.fetch_labels_list(conn_params)


@cross_origin
@app.route(ROOT + "/classifiers/<string:project>", methods=["GET"])
def fetch_classifiers(project):
    """Retrieve list of trained classifiers for project"""
    project = escape(project)
    project_dir = Path(PROJECTS_DIR) / project

    return bilava.fetch_classifiers(str(project_dir))


@cross_origin
@app.route(
    ROOT + "/projections/<string:classifier>/<string:reduction>/<string:split_set>",
    methods=["GET"],
)
def fetch_projections(classifier: str, reduction: str, split_set: str):
    """Retrieve the projected images with 2D coordinates based on the reduction method"""
    # TODO: deal with mistakes
    classifier = escape(classifier)
    reduction = escape(reduction)
    split_set = escape(split_set)
    conn_params = ConnectionParams(
        host=environ.get("host"),
        port=environ.get("port"),
        dbname=environ.get("dbname"),
        user=environ.get("user"),
        password=environ.get("password"),
        schema=environ.get("schema"),
    )
    return bilava.fetch_images(conn_params, classifier, reduction, split_set)
