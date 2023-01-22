""" Code for training a new model or update an existing model """

from pathlib import Path
from os import makedirs, listdir
from typing import Tuple
import pandas as pd


from utils.label_encoder import label_encoder_target
from utils.calc_stat import calc_dataset_mean_std


import torch
from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.callbacks import LearningRateMonitor, ModelCheckpoint
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.loggers import WandbLogger

import wandb


import image_modalities_classifier.dataset as ds
from image_modalities_classifier.models.resnet import Resnet


class ModalityModelTrainer:
    """Trainer for image modality classifiers"""

    def __init__(
        self,
        dataset_filepath,
        images_path,
        output_dir,
        taxonomy,
        classifier_name,
        project,
        label_col: str = "label",
        model_name: str = "resnet18",
        gpus: int = 1,
        learning_rate: float = 0.0001,
        batch_size: int = 32,
        epochs: int = 0,
        seed: int = 443,
        num_workers: int = 16,
    ):
        self.data_path = Path(dataset_filepath)
        self.base_img_dir = Path(images_path)
        self.num_workers = num_workers
        self.seed = seed
        self.project = project
        self.learning_rate = learning_rate
        self.gpus = gpus
        self.classifier = classifier_name
        self.model_name = model_name
        self.epochs = epochs
        self.metric_monitor = "val_avg_loss"
        self.mode = "min"
        self.extension = ".pt"
        self.batch_size = batch_size
        self.label_col = label_col
        self.partition_col = "split_set"
        self.img_path_col = "img_path"
        self.taxonomy = taxonomy

        self.output_dir = Path(output_dir) / self.taxonomy / self.classifier
        makedirs(self.output_dir, exist_ok=True)
        self.version = self._get_version()

        self.data = pd.read_parquet(self.data_path)
        self.data = ds.utils.remove_small_classes(self.data, col_name=self.label_col)
        self.label_encoder, _ = label_encoder_target(
            self.data, target_col=self.label_col
        )

    def _get_version(self):
        models = [x for x in listdir(self.output_dir) if x[-3:] == ".pt"]
        return len(models) + 1

    def _calculate_dataset_stats(self) -> Tuple[float, float]:
        basic_transforms = ds.transforms.ModalityTransforms.basic_transforms()
        train_df = self.data[self.data[self.partition_col] == "TRAIN"]

        train_dataset = ds.image_dataset.ImageDataset(
            train_df,
            str(self.base_img_dir),
            transforms=basic_transforms,
            label_name=self.label_col,
            path_col=self.img_path_col,
        )

        mean, std = calc_dataset_mean_std(
            train_dataset, batch_size=self.batch_size, num_workers=self.num_workers
        )
        return mean, std

    def run(self):
        """Start the training loop"""
        seed_everything(self.seed)
        train_mean, train_std = self._calculate_dataset_stats()

        wandb.init()
        wandb_logger = WandbLogger(project=self.project, reinit=True)
        wandb_logger.experiment.save()

        output_run_path = self.output_dir
        # makedirs(output_run_path, exist_ok=False)

        # setup data
        datamodule = ds.image_datamodule.ImageDataModule(
            batch_size=self.batch_size,
            label_encoder=self.label_encoder,
            data_path=str(self.data_path),
            base_img_dir=str(self.base_img_dir),
            seed=self.seed,
            num_workers=self.num_workers,
            partition_col=self.partition_col,
            label_col=self.label_col,
            path_col=self.img_path_col,
            train_mean=train_mean,
            train_std=train_std,
        )
        datamodule.prepare_data()
        datamodule.setup()
        datamodule.set_seed()

        # Callbacks
        lr_monitor = LearningRateMonitor(logging_interval="epoch")
        early_stop_callback = EarlyStopping(
            monitor=self.metric_monitor,
            min_delta=0.0,
            patience=5,
            verbose=True,
            mode=self.mode,
        )

        checkpoint_callback = ModelCheckpoint(
            dirpath=output_run_path,
            filename=f"{self.classifier}_{self.version}",
            monitor=self.metric_monitor,
            mode=self.mode,
            save_top_k=1,
        )
        checkpoint_callback.FILE_EXTENSION = self.extension

        num_classes = len(self.label_encoder.classes_)

        model = Resnet(
            name=self.model_name,
            num_classes=num_classes,
            pretrained=True,
            fine_tuned_from="whole",
            lr=self.learning_rate,
            metric_monitor=self.metric_monitor,
            mode_scheduler=self.mode,
            class_weights=datamodule.class_weights,
            mean_dataset=train_mean,
            std_dataset=train_std,
        )
        if self.version > 1:
            # model = ResNetClass.load_from_checkpoint(self.output_dir/f'{self.classifier}_{self.version}.{self.extension}')
            # model.class_weights = dm.class_weights
            # model.mean_dataset = mean
            # model.std_dataset = std
            # self.save_hyperparameters("class_weights","mean_dataset","std_dataset")
            checkpoint = torch.load(
                self.output_dir / f"{self.classifier}_{self.version-1}{self.extension}"
            )
            model.load_state_dict(checkpoint["state_dict"])

        max_epochs = 100 if self.epochs == 0 else self.epochs
        callbacks = [lr_monitor, checkpoint_callback, early_stop_callback]
        trainer = Trainer(
            gpus=self.gpus,
            max_epochs=max_epochs,
            callbacks=callbacks,
            deterministic=True,
            logger=wandb_logger,
            num_sanity_val_steps=0,
        )
        trainer.fit(model, datamodule)

        wandb.finish()
        return f"{self.classifier}_{self.version}.{self.extension}"
