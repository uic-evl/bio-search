""" Code for training a new model or update an existing model 

Model versioning

The trainer receives a directory path to set where the trained model should be
stored. If there is any existing model in the directory (.pt), the trainer 
load the latest existing model and increments the version number. The versioning
syntax is very simple <taxonomy_name>_<classifier>_<version>, where version
is an integer.

"""

from pathlib import Path
from os import makedirs, listdir
from typing import Tuple
import pandas as pd
from sklearn.preprocessing import LabelEncoder

import torch
from torch.utils.data import DataLoader
from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.callbacks import LearningRateMonitor, ModelCheckpoint
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.loggers import WandbLogger

import wandb


import image_modalities_classifier.dataset as ds
from image_modalities_classifier.dataset.image_dataset import ImageDataset
from image_modalities_classifier.models.resnet import Resnet


ENCODED_COL_NAME = "enc_label"


def calc_ds_stats(
    dataset: ImageDataset, batch_size: int = 32, num_workers: int = 0
) -> Tuple[float, float]:
    """Calculate the mean and standard deviation over the pixels in the dataset"""
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        num_workers=num_workers,
        shuffle=False,
    )

    mean = 0.0
    for batch in loader:
        images = batch[0]
        batch_samples = images.size(0)
        images = images.view(batch_samples, images.size(1), -1)
        mean += images.mean(2).sum(0)
    mean = mean / len(loader.dataset)

    var = 0.0
    image_info = dataset[0]
    sample_img = image_info[0]
    # for std calculations
    height, width = sample_img.shape[1], sample_img.shape[2]

    for batch in loader:
        images = batch[0]
        batch_samples = images.size(0)
        images = images.view(batch_samples, images.size(1), -1)
        var += ((images - mean.unsqueeze(1)) ** 2).sum([0, 2])
    std = torch.sqrt(var / (len(loader.dataset) * width * height))

    return mean, std


class ModalityModelTrainer:
    """Trainer for image modality classifiers

    Attributes
    ----------
    dataset_filepath: str
        File path to the parquet file with the training, validation, and test data.
    base_img_dir: str
        Relative path where all the images are stored on disk, such that by
        contatenating base_img_dir and the path in the dataset_filepath, the
        trainer can access to the image.
    output_dir: str
        Location where to save the model weights.
    taxonomy: str
        Name of the taxonomy used in the project. Used for setting up the output
        directory and saving the metadata.
    classifier_name: str
        As expected. Used for setting up the output directory and saving metadata
    project: str
        Project name to organize model tracking on wandb

    """

    def __init__(
        self,
        dataset_filepath,
        base_img_dir,
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
        self.base_img_dir = Path(base_img_dir)
        self.project = project
        self.num_workers = num_workers
        self.seed = seed
        # attributes mostly related
        self.model_name = model_name
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.gpus = gpus
        self.batch_size = batch_size

        self.label_col = label_col
        self.artifacts_dir = output_dir
        self.classifier = classifier_name
        self.taxonomy = taxonomy

        self.metric_monitor = "val_avg_loss"
        self.mode = "min"
        self.extension = ".pt"
        self.partition_col = "split_set"
        self.img_path_col = "img_path"

        self.data = None
        self.encoder = None
        self.output_dir = None
        self.version = None

    def _prepare_data(self):
        self.data = pd.read_parquet(self.data_path)
        self.data = ds.utils.remove_small_classes(self.data, col_name=self.label_col)
        self._encode_dataset()

    def _create_artifacts_folder(self):
        self.output_dir = Path(self.artifacts_dir) / self.taxonomy / self.classifier
        makedirs(self.output_dir, exist_ok=True)
        self.version = self._get_version()

    def _encode_dataset(self) -> None:
        """Created a column for holding the encoded label value and sets the
        label encoder with the classes in alphabetical order"""
        self.encoder = LabelEncoder()
        unique_labels = sorted(self.data[self.label_col].unique())
        if None in unique_labels:
            raise Exception(
                f"Data file has None values on the ${self.label_col} column"
            )
        self.encoder.fit(unique_labels)
        self.data[ENCODED_COL_NAME] = self.encoder.transform(self.data.values)

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

        mean, std = calc_ds_stats(
            train_dataset, batch_size=self.batch_size, num_workers=self.num_workers
        )
        return mean, std

    def run(self):
        """Start the training loop"""
        seed_everything(self.seed)
        self._prepare_data()
        self._create_artifacts_folder()
        train_mean, train_std = self._calculate_dataset_stats()

        wandb.init()
        wandb_logger = WandbLogger(project=self.project, reinit=True)
        wandb_logger.experiment.save()

        output_run_path = self.output_dir
        # makedirs(output_run_path, exist_ok=False)

        # setup data
        datamodule = ds.image_datamodule.ImageDataModule(
            batch_size=self.batch_size,
            label_encoder=self.encoder,
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

        num_classes = len(self.encoder.classes_)

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
