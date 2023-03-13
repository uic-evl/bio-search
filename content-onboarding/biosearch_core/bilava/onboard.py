from sys import argv
from os import makedirs
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Dict
import datetime
import logging

from biosearch_core.bilava import process_figures
from biosearch_core.bilava.classifier import Classifier
from biosearch_core.db.model import ConnectionParams, params_from_env

base_classifiers_dir = (
    "/mnt/curation_data/modality_classifiers_production/models/cord19"
)

classifiers = {
    "gel": {
        "longname": "gel",
        "shortname": "exp.gel",
        "model": base_classifiers_dir + "/gel/efficientnet-b1_gel_0.pt",
    },
    "higher-modality": {
        "longname": "higher-modality",
        "shortname": "",
        "model": base_classifiers_dir
        + "/higher-modality/efficientnet-b1_higher-modality_0.pt",
    },
    "experimental": {
        "longname": "experimental",
        "shortname": "exp",
        "model": base_classifiers_dir
        + "/experimental/efficientnet-b1_experimental_0.pt",
    },
    "graphics": {
        "longname": "graphics",
        "shortname": "gra",
        "model": base_classifiers_dir + "/graphics/efficientnet-b1_graphics_0.pt",
    },
    "microscopy": {
        "longname": "microscopy",
        "shortname": "mic",
        "model": base_classifiers_dir + "/microscopy/efficientnet-b0_microscopy_0.pt",
    },
    "electron": {
        "longname": "electron",
        "shortname": "mic.ele",
        "model": base_classifiers_dir + "/electron/efficientnet-b1_electron_0.pt",
    },
    "molecular": {
        "longname": "molecular",
        "shortname": "mol",
        "model": base_classifiers_dir + "/molecular/efficientnet-b1_molecular_0.pt",
    },
    "radiology": {
        "longname": "radiology",
        "shortname": "rad",
        "model": base_classifiers_dir + "/radiology/efficientnet-b0_radiology_0.pt",
    },
    "photography": {
        "longname": "photography",
        "shortname": "pho",
        "model": base_classifiers_dir + "/photography/resnet34_photography_0.pt",
    },
}

schemas_2_base_img_dir = {
    "training": "/mnt/curation_data",
    "cord19": "/mnt/biosearch/cord19/to_predict",
}


def setup_logger(workspace: str):
    """configure logger"""
    logger_dir = Path(workspace) / "logs"
    makedirs(logger_dir, exist_ok=True)

    logging.basicConfig(
        filename=str(logger_dir / "onboard.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def parse_args(args) -> Namespace:
    """Parse args from command line"""
    parser = ArgumentParser(prog="onboarding training data")
    parser.add_argument("bilava_dir", type=str, help="bilava folder")
    parser.add_argument("parquets_dir", type=str)
    parser.add_argument("db", type=str, help="path to .env with db conn")
    parser.add_argument("--batch_size", type=int, default=32)
    parsed_args = parser.parse_args(args)

    return parsed_args


def onboard_per_classifier(
    conn_params: ConnectionParams,
    workdir: str,
    clf_metadata: Classifier,
    parquets_dir: str,
    schemas_2_img_dir: Dict[str, str],
    schemas: List[str],
    batch_size: int,
):
    processed_df = process_figures.onboard_to_df(
        conn_params,
        workdir,
        clf_metadata,
        parquets_dir,
        schemas_2_img_dir,
        schemas,
        batch_size=batch_size,
    )
    return processed_df


def main():
    args = parse_args(argv[1:])
    setup_logger(str(Path(args.bilava_dir) / "logs"))
    conn_params = params_from_env(args.db)

    workdir = Path(args.bilava_dir) / datetime.datetime.now().strftime("%Y%M%D%h%m%s")
    makedirs(workdir)

    # pylint: disable=consider-iterating-dictionary, consider-using-dict-items
    for clf_key in classifiers.keys():
        meta = classifiers[clf_key]
        clf = Classifier(
            long_name=meta["longname"],
            short_name=meta["shortname"],
            model_path=meta["model"],
        )
        try:
            onboard_per_classifier(
                conn_params,
                str(workdir),
                clf,
                args.parquets_dir,
                schemas_2_base_img_dir,
                ["training", "cord19"],
                args.batch_size,
            )
        # pylint: disable=bare-except,broad-exception-caught
        except Exception:
            logging.error("Error %s", clf.long_name, exc_info=True)


if __name__ == "__main__":
    main()
