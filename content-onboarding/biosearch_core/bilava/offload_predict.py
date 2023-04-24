""" Script to perform the updates on all figures  """

from sys import argv
from os import makedirs
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict
import logging
import json
from biosearch_core.prediction.predictor import PredictManager
from biosearch_core.db.model import params_from_env


def setup_logger(workspace: str):
    """configure logger"""
    logger_dir = Path(workspace) / "logs"
    if not logger_dir.exists:
        makedirs(logger_dir)

    logging.basicConfig(
        filename=str(logger_dir / "offload_predictions.log"),
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
    # fmt: off
    parser = ArgumentParser(prog="BI-LAVA label updater")
    parser.add_argument("bilava_dir", type=str, help="dir to bilava artifacts")
    parser.add_argument("db", type=str, help="path to .env with db conn")
    parser.add_argument("-clfs", "--classifiers", type=str, help="json file with classifiers to use", required=True)
    parser.add_argument("-ds", "--data_schemas", nargs="+", help="schemas for for figures to predict", required=True)
    parser.add_argument("-i", "--imgs_path", help="base path for images", required=True)
    parsed_args = parser.parse_args(args)
    # fmt: on

    return parsed_args


def main():
    """main entry"""
    args = parse_args(argv[1:])
    print(args)
    base_img_path = args.imgs_path
    conn_params = params_from_env(args.db)
    setup_logger(args.bilava_dir)

    classifiers = load_classifiers_info(args.classifiers)

    for data_schema in args.data_schemas:
        conn_params.schema = data_schema
        if "cord19" in data_schema:
            imgs_path = str(Path(base_img_path) / "biosearch" / "cord19" / "to_predict")
        else:
            imgs_path = base_img_path

        print(f"\nProcessing {data_schema}\n")
        manager = PredictManager(imgs_path, conn_params, classifiers)
        manager.predict_and_update_db(status=None)  # update all images


if __name__ == "__main__":
    main()
