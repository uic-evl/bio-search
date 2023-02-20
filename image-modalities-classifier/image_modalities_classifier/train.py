""" Entry script for training modality models """
from sys import argv
from os import listdir
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional, List

import logging

from image_modalities_classifier.models.trainer import ModalityModelTrainer


def find_latest_dataset(workspace: str, taxonomy: str, classifier: str) -> str:
    """Search for the corresponding parquet file in the workspace"""
    container_path = Path(workspace) / "data" / taxonomy
    prefix = f"{taxonomy}_{classifier}_v"
    parquet_files = [
        file
        for file in listdir(container_path)
        if file.startswith(prefix) and file.endswith(".parquet")
    ]
    parquet_files = sorted(parquet_files, reverse=True)
    if len(parquet_files) == 0:
        raise Exception(
            f"No data found for classifier {classifier} in {container_path}"
        )
    data_file = str(container_path / parquet_files[0])
    logging.info("data_file: %s", data_file)
    return data_file


def train(
    workspace: str,
    taxonomy: str,
    classifier: str,
    base_img_dir: str,
    model: str,
    project: str,
    learning_rate: float,
    num_workers: int,
    epochs: int,
    pseudo: bool,
    mean: Optional[List[float]],
    std: Optional[List[float]],
    patience: Optional[int],
):
    """Train the model"""
    dataset_path = find_latest_dataset(workspace, taxonomy, classifier)
    output_dir = str(Path(workspace) / "models")
    trainer = ModalityModelTrainer(
        dataset_path,
        base_img_dir,
        output_dir,
        taxonomy,
        classifier,
        project,
        num_workers=num_workers,
        model_name=model,
        learning_rate=learning_rate,
        epochs=epochs,
        use_pseudo=pseudo,
        mean=mean,
        std=std,
        remove_small=False,
        patience=patience,
    )
    trainer.run()


def setup_logger(workspace: str):
    """configure logger"""
    logger_dir = Path(workspace)
    if not logger_dir.exists:
        raise Exception("workspace does not exist")

    logging.basicConfig(
        filename=str(logger_dir / "training.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def parse_args(args) -> Namespace:
    """Read arguments from command line
    classifier: one of microscopy | electron | graphics | experimental |
      molecular | radiology
    model: one of resnet18 | resnet34 | resnet50 | resnet101 | resnet152
    workspace: file directory where we are storing the artifacts and where to
      find the data. It has the structure:
      /workspace
        /data
          /taxonomy
            some_data.parquet
        /models
          /taxonomy
            classifier
              model_x.pt
    """
    parser = ArgumentParser(prog="modality classifier trainer")
    parser.add_argument("classifier", type=str, help="classifier name")
    parser.add_argument("model", type=str, help="Resnet model")
    parser.add_argument("workspace", type=str)
    parser.add_argument("base_img_dir", type=str)
    parser.add_argument("--lr", "-l", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--num_workers", "-w", type=int, default=4)
    parser.add_argument("--taxonomy", "-t", type=str, default="cord19")
    parser.add_argument("--project", "-p", type=str, default="biocuration")
    parser.add_argument("--epochs", "-e", type=int, default=1)
    parser.add_argument("--pseudo", dest="pseudo", action="store_true")
    parser.add_argument("--no-pseudo", dest="pseudo", action="store_false")
    parser.add_argument("--patience", type=int, default=None)
    parser.add_argument(
        "--mean", "-m", type=float, nargs="+", default=None, help="Dataset mean"
    )
    parser.add_argument(
        "--std", "-s", type=float, nargs="+", default=None, help="Dataset std"
    )
    parser.set_defaults(feature=False)

    return parser.parse_args(args)


def verify_stats(name: str, stat: Optional[List[float]]):
    """validate stats are array of 3 elements, one per RGB channel"""
    if stat is not None and len(stat) != 3:
        message = f"{name} should be an array of 3 elements"
        raise Exception(message)


def main():
    """main entry point"""
    args = parse_args(argv[1:])
    classifier_name = args.classifier
    setup_logger(args.workspace)

    verify_stats("mean", args.mean)
    verify_stats("std", args.std)

    try:
        train(
            args.workspace,
            args.taxonomy,
            classifier_name,
            args.base_img_dir,
            args.model,
            args.project,
            args.lr,
            args.num_workers,
            args.epochs,
            args.pseudo,
            args.mean,
            args.std,
            args.patience,
        )
    # pylint: disable=broad-except
    except Exception:
        message = f"{classifier_name}: training failed"
        logging.error(message, exc_info=True)


if __name__ == "__main__":
    main()
