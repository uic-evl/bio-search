""" Functions to support bilava back-end"""
from pathlib import Path
from typing import List, Literal, Dict
import json
import logging
from psycopg import connect
from psycopg.rows import dict_row
from biosearch_core.db.model import ConnectionParams


def fetch_classifiers(project_dir: str) -> List[str]:
    """Load the taxonomy list from the project definitions"""
    classifiers_path = Path(project_dir) / "definitions" / "classifiers.json"
    try:
        with open(classifiers_path, "r", encoding="utf-8") as f_in:
            classifiers_info = json.load(f_in)
        classifiers = []
        fringe = [classifiers_info]
        while len(fringe) > 0:
            node = fringe.pop(0)
            classifiers.append(node["classifier"])
            for child in node["children"]:
                fringe.append(child)
        return classifiers
    except FileNotFoundError:
        logging.error("File not found %s", classifiers_path, exc_info=True)
        return None


def fetch_labels_list(conn_params: ConnectionParams) -> List[str]:
    """Fetch labels from database to fit the taxonomy tree"""

    labels = None
    # pylint: disable=not-context-manager
    with connect(conninfo=conn_params.conninfo()) as conn:
        with conn.cursor() as cursor:
            try:
                query = f"SELECT label from {conn_params.schema}.figures"
                cursor.execute(query)
                labels = cursor.fetchall()
                labels = [elem[0] for elem in labels]
            # pylint: disable=broad-except
            except Exception as exc:
                print("Erorr fetching labels", exc)
                logging.error("Error fetching labels", exc_info=True)
    return labels


classifiers_mapper = {
    "experimental": "exp",
    "gel": "exp.gel",
    "higher-modality": "",
    "microscopy": "mic",
    "molecular": "mol",
    "graphics": "gra",
    "radiology": "rad",
    "photography": "pho",
    "electron": "mic.ele",
}


def fetch_images(
    conn_params: ConnectionParams,
    classifier: str,
    reduction: Literal["pca", "umap", "tsne"],
    split_set: Literal["TRAIN", "VAL", "TEST", "UNL", "ALL"],
    schemas_2_base_img_dir: Dict[str, str],
    image_server: str,
):
    """Fetch images from database for projection view"""

    images = None
    lbl_len = len(classifiers_mapper[classifier]) + 4  # . and next level

    # pylint: disable=not-context-manager
    with connect(conninfo=conn_params.conninfo(), row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            try:
                query = """
                 SELECT id, uri, prediction as prd, 
                        LEFT(label, {lbl_len}) as lbl,
                        ROUND(x_{reduction}, 2)::float as x,
                        ROUND(y_{reduction}, 2)::float as y,
                        ROUND(hit_{reduction}, 2)::float as hit,
                        split_set as ss,
                        schema
                 FROM {bilava_schema}.features
                 WHERE classifier = '{classifier}'
                """.format(
                    reduction=reduction,
                    classifier=classifier,
                    bilava_schema=conn_params.schema,
                    lbl_len=lbl_len,
                )
                if split_set != "ALL":
                    query = f"{query} AND split_set='{split_set}'"

                cursor.execute(query)
                images = cursor.fetchall()
                images = [
                    {
                        "id": el["id"],
                        "lbl": el["lbl"],
                        "prd": el["prd"],
                        "uri": f"{image_server}/{schemas_2_base_img_dir[el['schema']]}/{el['uri']}",
                        "x": el["x"],
                        "y": el["y"],
                        "hit": el["hit"],
                        "ss": el["ss"],
                    }
                    for el in images
                ]
            # pylint: disable=broad-except
            except Exception as exc:
                print("Erorr fetching labels", exc)
                logging.error("Error fetching labels", exc_info=True)
    return images
