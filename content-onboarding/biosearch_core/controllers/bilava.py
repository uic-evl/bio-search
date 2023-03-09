""" Functions to support bilava back-end"""
from pathlib import Path
from typing import List
import json
import logging
from psycopg import connect
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
