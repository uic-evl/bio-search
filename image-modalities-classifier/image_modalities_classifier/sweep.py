from sys import argv
from pathlib import Path
import logging
from typing import Optional
from functools import partial
from argparse import ArgumentParser, Namespace
from datetime import datetime
import wandb
from image_modalities_classifier.train import train

# big hm [0.7562, 0.7535, 0.7540]
# [0.3078, 0.3037, 0.3088]

# mean grpahics 400 0.9248, 0.9202, 0.9211
# std graphics 400 0.2077, 0.2006, 0.2128

means_per_clf_name = {
    "higher-modality": [0.7687, 0.7660, 0.7663],
    "microscopy": [0.4951, 0.4829, 0.4857],
    "electron": [0.5759, 0.5745, 0.5730],
    "radiology": [0.4981, 0.4983, 0.4984],
    "photography": [0.5442, 0.4407, 0.4029],
    "graphics": [0.9218, 0.9174, 0.9180],
    "experimental": [0.8608, 0.8608, 0.8612],
    "gel": [0.7912, 0.7917, 0.7922],
    "molecular": [0.8662, 0.8683, 0.8588],
}

stds_per_clf_name = {
    "higher-modality": [0.3024, 0.2991, 0.3034],
    "microscopy": [0.3524, 0.3438, 0.3545],
    "electron": [0.2657, 0.2672, 0.2677],
    "radiology": [0.2521, 0.2521, 0.2521],
    "photography": [0.2892, 0.2658, 0.2690],
    "graphics": [0.2046, 0.1995, 0.2094],
    "experimental": [0.2348, 0.2346, 0.2345],
    "gel": [0.2566, 0.2563, 0.2558],
    "molecular": [0.2439, 0.2386, 0.2547],
}

sweep_configuration_efficientnet = {
    "method": "grid",
    "metric": {"goal": "minimize", "name": "val_loss"},
    "parameters": {
        "batch_size": {"values": [32]},
        "epochs": {"values": [100]},
        "lr": {"values": [1e-3]},
        "pretrained": {"values": [True]},
        "model": {
            "values": [
                "efficientnet-b1",
                "resnet18",
                # "resnet18",
                # "resnet34",
                # "resnet50",
                # "resnet101",
            ]
        },
        "patience": {"values": [10]},
    },
}

sweep_configuration_resnet = {
    "method": "grid",
    "metric": {"goal": "minimize", "name": "val_loss"},
    "parameters": {
        "batch_size": {"values": [32]},
        "epochs": {"values": [100]},
        "lr": {"values": [1e-3]},
        "pretrained": {"values": [True, False]},
        "model": {"values": ["resnet18", "resnet34", "resnet50"]},
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
    gpus: int,
    precision: int,
    strategy: Optional[str],
):
    """Function to invoke on each sweep iteration"""
    project = "biocuration"

    # start wandb for logging stats
    group = None
    if strategy == "ddp":
        group = "ddp"

    try:
        run = wandb.init(project=project, group=group)
        run.tags = [clf_name, wandb.config.model]
        train(
            classifier=clf_name,
            workspace=workspace,
            taxonomy=taxonomy,
            model=wandb.config.model,
            base_img_dir=base_img_dir,
            project=project,
            learning_rate=wandb.config.lr,
            num_workers=num_workers,
            epochs=wandb.config.epochs,
            pseudo=False,
            mean=means_per_clf_name[clf_name],
            std=means_per_clf_name[clf_name],
            patience=wandb.config.patience,
            pretrained=wandb.config.pretrained,
            batch_size=wandb.config.batch_size,
            gpus=gpus,
            precision=precision,
            strategy=strategy,
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
    gpus: int,
    precision: int,
    strategy: Optional[str],
):
    """Load sweep config and run agent"""
    # make partial to only depend on wandb.config attributes
    sweep_iteration = partial(
        train_iteration,
        clf_name,
        workspace,
        taxonomy,
        base_img_dir,
        num_workers,
        gpus,
        precision,
        strategy,
    )

    project = "biocuration"
    sweep_eff_id = wandb.sweep(sweep_configuration_efficientnet, project=project)
    wandb.agent(sweep_eff_id, function=sweep_iteration)
    # sweep_res_id = wandb.sweep(sweep_configuration_resnet, project=project)
    # wandb.agent(sweep_res_id, function=sweep_iteration)


def parse_args(args) -> Namespace:
    """Read arguments from command line"""
    parser = ArgumentParser(prog="modality classifier trainer")
    parser.add_argument("classifier", type=str, help="classifier name")
    parser.add_argument("workspace", type=str)
    parser.add_argument("base_img_dir", type=str)
    parser.add_argument("--num_workers", "-w", type=int, default=4)
    parser.add_argument("--taxonomy", "-t", type=str, default="cord19")
    parser.add_argument("--gpus", type=int, default=1)
    parser.add_argument("--precision", type=int, default=32)
    parser.add_argument("--strategy", type=str, default=None)

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
        gpus=args.gpus,
        precision=args.precision,
        strategy=args.strategy,
    )


if __name__ == "__main__":
    main()
