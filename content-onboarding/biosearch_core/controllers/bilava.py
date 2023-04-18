""" Functions to support bilava back-end"""
from pathlib import Path
from typing import List, Literal, Dict
from datetime import datetime
import json
import logging
from psycopg import connect, sql
from psycopg.rows import dict_row
from biosearch_core.db.model import ConnectionParams
from biosearch_core.data.figure import SubFigureStatus


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
    split_set: Literal["TRAIN", "TRAIN+UNL", "VAL", "TEST", "UNL", "ALL"],
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
                        schema,
                        width,
                        height,
                        ms,
                        en,
                        source,
                        round((SELECT max(probs) from unnest(pred_probs) as probs),2)::float as max_prob,
                        status::int,
                        upt_label
                 FROM {bilava_schema}.features
                 WHERE classifier = '{classifier}' AND (upt_label IS NULL OR upt_label NOT LIKE 'error%')
                """.format(
                    reduction=reduction,
                    classifier=classifier,
                    bilava_schema=conn_params.schema,
                    lbl_len=lbl_len,
                )
                if split_set != "ALL":
                    if split_set == "TRAIN+UNL":
                        query = f"{query} AND (split_set='TRAIN' OR split_set='UNL')"
                    else:
                        query = f"{query} AND split_set='{split_set}'"

                cursor.execute(query)
                images = cursor.fetchall()

                images = [
                    {
                        "dbId": el["id"],
                        "lbl": el["lbl"]
                        if el["status"] == SubFigureStatus.GROUND_TRUTH.value
                        else "unl",
                        "prd": el["prd"],
                        "uri": f"{image_server}/{schemas_2_base_img_dir[el['schema']]}/{el['uri']}",
                        "x": el["x"],
                        "y": el["y"],
                        "hit": el["hit"],
                        "ss": el["ss"],
                        "w": el["width"],
                        "h": el["height"],
                        "ms": el["ms"],
                        "en": el["en"],
                        "sr": el["source"],
                        "mp": el["max_prob"],
                        "ulbl": el["upt_label"],
                    }
                    for el in images
                ]
                unique_labels = list(set(el["lbl"] for el in images))
                if "unl" in unique_labels:
                    unique_labels.remove("unl")
                sources = list(set(el["sr"] for el in images))
                unique_labels.sort()
                sources.sort()
                min_prediction = min([el["mp"] for el in images])
            # pylint: disable=broad-except
            except Exception as exc:
                print("Error fetching labels", exc)
                logging.error("Error fetching labels", exc_info=True)
    return {
        "data": images,
        "labels": unique_labels,
        "sources": sources,
        "minPrediction": min_prediction,
    }


def fetch_image_extras(conn_params: ConnectionParams, db_id: int, classifier: str):
    """Fetch information for the thumbnail details panel"""
    # pylint: disable=not-context-manager
    with connect(conninfo=conn_params.conninfo(), row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            try:
                # pylint: disable=C0209:consider-using-f-string
                query = """
                    SELECT name, pred_probs, source
                    FROM {bilava_schema}.features 
                    WHERE id={db_id} AND classifier='{classifier}'
                """.format(
                    bilava_schema=conn_params.schema, db_id=db_id, classifier=classifier
                )
                cursor.execute(query)
                image = cursor.fetchall()[0]

                if image["source"] == "gdx" or image["source"] == "cord19":
                    query_caption = """
                        SELECT sf.label as lbl, f.caption 
                        FROM {schema}.figures sf, {schema}.figures f 
                        WHERE sf.id={db_id} AND f.id = sf.parent_id
                    """.format(
                        schema=image["source"], db_id=db_id
                    )
                else:
                    caption_schema = "training"
                    query_caption = f"SELECT ground_truth as lbl, caption FROM {caption_schema}.figures WHERE id={db_id}"

                cursor.execute(query_caption)
                record = cursor.fetchall()[0]

                return {
                    "name": image["name"],
                    "probs": [round(float(el), 3) for el in image["pred_probs"]],
                    "caption": record["caption"],
                    "fullLabel": record["lbl"],
                }
            # pylint: disable=broad-except
            except Exception as exc:
                print("Error fetching image extra", exc)
                logging.error("Error fetching image extra", exc_info=True)


def update_image_labels(
    conn_params: ConnectionParams, ids: List[int], label: str
) -> bool:
    """Update the upt_label column with the user specified value. We do not touch
    the label value yet as this column will be updated during the next iteration
    """
    query_params = [(datetime.now(), dbid) for dbid in ids]
    flattened_values = [item for sublist in query_params for item in sublist]

    single_query = f"UPDATE {conn_params.schema}.features SET upt_label='{label}', "
    single_query += "upt_date=('{}') WHERE id=({}); "  # the placeholder

    # pylint: disable=not-context-manager
    with connect(conninfo=conn_params.conninfo(), autocommit=False) as conn:
        with conn.cursor() as cursor:
            try:
                all_queries = single_query * len(query_params)
                query = sql.SQL(all_queries.format(*flattened_values))
                cursor.execute(query)
                conn.commit()
                return True
            # pylint: disable=broad-except
            except Exception as exc:
                print("Error updating features in database", exc)
                logging.error("Error updating features in database", exc_info=True)
                return False
