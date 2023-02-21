from sys import argv
from pathlib import Path
import logging
from functools import partial
from argparse import ArgumentParser, Namespace
import wandb
from image_modalities_classifier.train import train

means_per_clf_name = {
    "higher-modality": [],
    "microscopy": [0.4951, 0.4829, 0.4857],
    "electron": [0.5759, 0.5745, 0.5730],
    "radiology": [0.4981, 0.4983, 0.4984],
    "photography": [],
    "graphics": [],
    "experimental": [0.8608, 0.8608, 0.8612],
    "gel": [],
    "molecular": [],
}

stds_per_clf_name = {
    "higher-modality": [],
    "microscopy": [0.3524, 0.3438, 0.3545],
    "electron": [0.2657, 0.2672, 0.2677],
    "radiology": [0.2521, 0.2521, 0.2521],
    "photography": [],
    "graphics": [],
    "experimental": [0.2348, 0.2346, 0.2345],
    "gel": [],
    "molecular": [],
}

sweep_configuration = {
    "method": "grid",
    "metric": {"goal": "minimize", "name": "val_loss"},
    "parameters": {
        "batch_size": {"values": [128]},
        "epochs": {"values": [100]},
        "lr": {"values": [0.016, 1e-3]},
        "pretrained": {"values": [True, False]},
        "model": {
            "values": [
                "resnet18",
                "resnet34",
                "resnet50",
                "efficientnet-b0",
                "efficientnet-b1",
            ]
        },
        "patience": {"values": [20]},
    },
}


def setup_logger(workspace: str):
    """configure logger"""
    logger_dir = Path(workspace)
    if not logger_dir.exists:
        # pylint: disable=broad-exception-raised
        raise Exception("workspace does not exist")

    logging.basicConfig(
        filename=str(logger_dir / "training.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def train_iteration(
    clf_name: str,
    workspace: str,
    taxonomy: str,
    base_img_dir: str,
    num_workers: int,
):
    """Function to invoke on each sweep iteration"""
    wandb.init()
    try:
        train(
            classifier=clf_name,
            workspace=workspace,
            taxonomy=taxonomy,
            model=wandb.config.model,
            base_img_dir=base_img_dir,
            project=f"biocuration-{clf_name}",
            learning_rate=wandb.config.lr,
            num_workers=num_workers,
            epochs=wandb.config.epochs,
            pseudo=False,
            mean=means_per_clf_name[clf_name],
            std=means_per_clf_name[clf_name],
            patience=wandb.config.patience,
            pretrained=wandb.config.pretrained,
            batch_size=wandb.config.batch_size,
        )
    # pylint: disable=broad-except
    except Exception:
        message = f"{clf_name}: training failed"
        logging.error(message, exc_info=True)


def execute_sweeps(
    clf_name: str,
    workspace: str,
    taxonomy: str,
    base_img_dir: str,
    num_workers: int,
):
    """Load sweep config and run agent"""
    project = f"biocuration-{clf_name}"
    sweep_id = wandb.sweep(sweep_configuration, project=project)

    # make partial to only depend on wandb.config attributes
    sweep_iteration = partial(
        train_iteration,
        clf_name,
        workspace,
        taxonomy,
        base_img_dir,
        num_workers,
    )
    wandb.agent(sweep_id, function=sweep_iteration)


def parse_args(args) -> Namespace:
    """Read arguments from command line"""
    parser = ArgumentParser(prog="modality classifier trainer")
    parser.add_argument("classifier", type=str, help="classifier name")
    parser.add_argument("workspace", type=str)
    parser.add_argument("base_img_dir", type=str)
    parser.add_argument("--num_workers", "-w", type=int, default=4)
    parser.add_argument("--taxonomy", "-t", type=str, default="cord19")

    return parser.parse_args(args)


def main():
    """Main entry"""
    args = parse_args(argv[1:])
    setup_logger(args.workspace)
    execute_sweeps(
        clf_name=args.classifier,
        workspace=args.workspace,
        taxonomy=args.taxonomy,
        base_img_dir=args.base_img_dir,
        num_workers=args.num_workers,
    )


if __name__ == "__main__":
    main()
