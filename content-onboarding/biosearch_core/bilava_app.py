""" Flask API for the search interface """

from os import environ
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from markupsafe import escape
from werkzeug.exceptions import BadRequest, InternalServerError
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

# this should come from the configuration file
schemas_2_base_img_dir = {
    "training": "curation_data",
    "cord19": "biosearch/cord19/to_predict",
}


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    """Handler for cases when the parameters are wrong"""
    response = {"description": e.description}
    return jsonify(response), 400


@app.errorhandler(InternalServerError)
def handle_internal_server_error(e):
    """Handler for cases when the code raised an exception"""
    response = {"description": e.description}
    return jsonify(response), 500


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
    # pylint: disable=too-many-function-args
    return bilava.fetch_images(
        conn_params,
        classifier,
        reduction,
        split_set,
        schemas_2_base_img_dir,
        environ.get("IMAGE_HOST"),
    )


@cross_origin
@app.route(
    ROOT + "/images/<int:img_id>/<string:classifier>/extras",
    methods=["GET"],
)
def fetch_extra_image_info(img_id: int, classifier: str):
    """Retrieve additional information for image"""
    img_id = escape(img_id)
    classifier = escape(classifier)
    conn_params = ConnectionParams(
        host=environ.get("host"),
        port=environ.get("port"),
        dbname=environ.get("dbname"),
        user=environ.get("user"),
        password=environ.get("password"),
        schema=environ.get("schema"),
    )
    return bilava.fetch_image_extras(conn_params, img_id, classifier)


@cross_origin
@app.route(ROOT + "/images/batch_update", methods=["POST"])
def batch_update_labels():
    """Batch update figures from bilava"""
    inputs = request.json
    if (
        "ids" in inputs
        and "label" in inputs
        and len(inputs["ids"]) > 0
        and inputs["label"].strip() != ""
    ):
        conn_params = ConnectionParams(
            host=environ.get("host"),
            port=environ.get("port"),
            dbname=environ.get("dbname"),
            user=environ.get("user"),
            password=environ.get("password"),
            schema=environ.get("schema"),
        )
        result = bilava.update_image_labels(conn_params, inputs["ids"], inputs["label"])
        if not result:
            raise InternalServerError("Error executing updates")
        else:
            return {"total_updates": len(inputs["ids"])}
    else:
        raise BadRequest("invalid parameters")
