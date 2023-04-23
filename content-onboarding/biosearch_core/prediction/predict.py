""" Fetch subfigures with status unpredicted and predict the modality """

from sys import argv
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict
import logging
import json
from biosearch_core.data.figure import SubFigureStatus
from biosearch_core.prediction.predictor import PredictManager
from biosearch_core.db.model import params_from_env


def setup_logger(workspace: str):
    """configure logger"""
    logger_dir = Path(workspace) / "logs"
    if not logger_dir.exists:
        raise FileNotFoundError("workspace does not exist")

    logging.basicConfig(
        filename=str(logger_dir / "predict_labels.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def load_classifiers_info(definition_path: str) -> Dict:
    """Load json file with classifiers info"""
    with open(definition_path, "r", encoding="utf-8") as input_file:
        json_data = json.load(input_file)
        # TODO validate everything exists
        return json_data


def parse_args(args) -> Namespace:
    """Parse args from command line"""
    parser = ArgumentParser(prog="DB Importer")
    parser.add_argument(
        "projects_dir", type=str, help="root folder where projects are stored"
    )
    parser.add_argument("project", type=str, help="project name")
    parser.add_argument("db", type=str, help="path to .env with db conn")
    parser.add_argument(
        "classifiers", type=str, help="json file with classifiers to use"
    )
    parsed_args = parser.parse_args(args)

    return parsed_args


def main():
    """main entry"""
    args = parse_args(argv[1:])
    project_dir = Path(args.projects_dir) / args.project
    conn_params = params_from_env(args.db)

    setup_logger(project_dir)
    classifiers = load_classifiers_info(args.classifiers)
    manager = PredictManager(str(project_dir), conn_params, classifiers)
    manager.predict_and_update_db(status=SubFigureStatus.NOT_PREDICTED)


if __name__ == "__main__":
    main()
