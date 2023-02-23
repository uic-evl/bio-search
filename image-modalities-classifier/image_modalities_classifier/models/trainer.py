""" Code for training a new model or update an existing model 

Model versioning

The trainer receives a directory path to set where the trained model should be
stored. If there is any existing model in the directory (.pt), the trainer 
load the latest existing model and increments the version number. The versioning
syntax is very simple <taxonomy_name>_<classifier>_<version>, where version
is an integer.

"""

from pathlib import Path
from os import makedirs, listdir, cpu_count
from datetime import datetime
from typing import Tuple, List, Optional
from tqdm import tqdm
import pandas as pd
from sklearn.preprocessing import LabelEncoder

import torch
from torch.utils.data import DataLoader
from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.callbacks import LearningRateMonitor, ModelCheckpoint
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.loggers import WandbLogger

import wandb

from image_modalities_classifier.dataset.utils import remove_small_classes
from image_modalities_classifier.dataset.image_dataset import ImageDataset
from image_modalities_classifier.dataset.image_datamodule import ImageDataModule
from image_modalities_classifier.dataset.transforms import ModalityTransforms
from image_modalities_classifier.models.modality_module import ModalityModule


ENCODED_COL_NAME = "enc_label"


def calc_ds_stats(
    dataset: ImageDataset, batch_size: int = 512
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Calculate the mean and standard deviation over the pixels in the dataset
    https://www.binarystudy.com/2021/04/how-to-calculate-mean-standard-deviation-images-pytorch.html
    """
    num_workers = cpu_count()
    loader = DataLoader(dataset, batch_size=batch_size, num_workers=num_workers)

    cnt = 0
    fst_moment = torch.empty(3)
    snd_moment = torch.empty(3)

    for images, _ in tqdm(loader):
        # calcs with respect to the channels
        b_size, _, height, width = images.shape
        nb_pixels = b_size * height * width
        sum_ = torch.sum(images, dim=[0, 2, 3])
        sum_of_square = torch.sum(images**2, dim=[0, 2, 3])
        fst_moment = (cnt * fst_moment + sum_) / (cnt + nb_pixels)
        snd_moment = (cnt * snd_moment + sum_of_square) / (cnt + nb_pixels)
        cnt += nb_pixels

    mean, std = fst_moment, torch.sqrt(snd_moment - fst_moment**2)
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
        num_workers: int = 4,
        remove_small: bool = True,
        use_pseudo: bool = False,
        mean: List[float] = None,
        std: List[float] = None,
        patience: Optional[int] = None,
        pretrained: bool = False,
        precision: int = 32,
        strategy: Optional[str] = None,
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
        self.precision = precision
        self.strategy = strategy

        self.batch_size = batch_size
        self.mean = torch.Tensor(mean) if mean is not None else torch.Tensor()
        self.std = torch.Tensor(std) if mean is not None else torch.Tensor()
        self.patience = patience
        self.pretrained = pretrained

        self.label_col = label_col
        self.artifacts_dir = output_dir
        self.classifier = classifier_name
        self.taxonomy = taxonomy

        self.extension = ".pt"
        self.partition_col = "split_set"
        self.img_path_col = "img_path"
        self.use_pseudo = use_pseudo

        self.remove_small = remove_small
        self.data = None
        self.encoder = None
        self.output_dir: Path = None
        self.version = None

        seed_everything(self.seed)

    def _prepare_data(self):
        print("preparing data")
        self.data = pd.read_parquet(self.data_path, engine="pyarrow")
        self.data = self.data[self.data[self.partition_col] != "UNL"]
        if not self.use_pseudo:
            self.data = self.data[self.data.is_gt]
        if self.remove_small:
            self.data = remove_small_classes(self.data, col_name=self.label_col)
        self._encode_dataset()

    def _create_artifacts_folder(self):
        print("creating artifacts")
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
        self.data[ENCODED_COL_NAME] = self.encoder.transform(
            self.data[self.label_col].values
        )

    def _get_version(self):
        models = [x for x in listdir(self.output_dir) if x[-3:] == ".pt"]
        return len(models) + 1

    def _calculate_dataset_stats(self) -> Tuple[torch.Tensor, torch.Tensor]:
        if self.mean.nelement() == 3 and self.std.nelement() == 3:
            # do not calculate when values are passed
            print("mean", self.mean)
            print("std", self.std)
            return

        print("calculating dataset stats")
        basic_transforms = ModalityTransforms.basic_transforms(self.model_name)
        train_df = self.data[self.data[self.partition_col] == "TRAIN"]

        train_dataset = ImageDataset(
            train_df,
            str(self.base_img_dir),
            transforms=basic_transforms,
            label_col=self.label_col,
            path_col=self.img_path_col,
        )
        mean, std = calc_ds_stats(train_dataset, batch_size=self.batch_size)
        self.mean = mean
        self.std = std
        print("mean", self.mean)
        print("std", self.std)

    def _create_data_module(self, train_mean, train_std):
        datamodule = ImageDataModule(
            model_name=self.model_name,
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
        datamodule.setup("fit")
        return datamodule

    def _append_logger_name(self, cp_name: str, run_name: str):
        filename = self.output_dir / "logger.txt"
        with open(filename, "a", encoding="utf-8") as file:
            file.write(f"{cp_name},{run_name}\n")

    def run(self):
        """Start the training loop
        Logging the data
        https://github.com/Lightning-AI/lightning/issues/14054
        """
        self._prepare_data()
        self._create_artifacts_folder()
        self._calculate_dataset_stats()
        datamodule = self._create_data_module(self.mean, self.std)

        # start wandb for logging stats
        group = None
        if self.strategy == "ddp":
            now = datetime.now().strftime("%m%d%H%M%S")
            group = f"ddp-{now}"
        run = wandb.init(
            project=self.project, tags=[self.classifier, self.model_name], group=group
        )
        wandb_logger = WandbLogger(project=self.project, group=group)

        # Callbacks
        metric_monitor = "val_loss"
        lr_monitor = LearningRateMonitor(logging_interval="epoch")

        early_stop_callback = None
        if self.patience:
            early_stop_callback = EarlyStopping(
                monitor=metric_monitor,
                min_delta=0.0,
                patience=self.patience,
                verbose=True,
                mode="min",
            )

        cp_name = f"{self.model_name}_{self.classifier}_{self.version}"
        checkpoint_callback = ModelCheckpoint(
            dirpath=self.output_dir,
            filename=cp_name,
            monitor=metric_monitor,
            mode="min",
            save_top_k=1,
        )
        checkpoint_callback.FILE_EXTENSION = self.extension

        num_classes = len(self.encoder.classes_)
        model = ModalityModule(
            self.encoder.classes_,
            num_classes,
            name=self.model_name,
            pretrained=self.pretrained,
            fine_tuned_from="whole",
            lr=self.learning_rate,
            metric_monitor=metric_monitor,
            mode_scheduler="min",
            class_weights=datamodule.class_weights,
            mean_dataset=list(self.mean.numpy()),
            std_dataset=list(self.std.numpy()),
            patience=self.patience,
        )
        # if self.version > 1:
        #     # model = ResNetClass.load_from_checkpoint(self.output_dir/f'{self.classifier}_{self.version}.{self.extension}')
        #     # model.class_weights = dm.class_weights
        #     # model.mean_dataset = mean
        #     # model.std_dataset = std
        #     # self.save_hyperparameters("class_weights","mean_dataset","std_dataset")
        #     checkpoint = torch.load(
        #         self.output_dir / f"{self.classifier}_{self.version-1}{self.extension}"
        #     )
        #     model.load_state_dict(checkpoint["state_dict"])

        max_epochs = 100 if self.epochs == 0 else self.epochs
        callbacks = (
            [lr_monitor, checkpoint_callback, early_stop_callback]
            if early_stop_callback
            else [lr_monitor, checkpoint_callback]
        )

        strategy = self.strategy
        if self.strategy is not None and self.strategy == "ddp":
            strategy = "ddp_find_unused_parameters_false"

        trainer = Trainer(
            accelerator="gpu" if torch.cuda.is_available() else "cpu",
            devices=self.gpus,
            max_epochs=max_epochs,
            callbacks=callbacks,
            deterministic=True,
            logger=wandb_logger,
            num_sanity_val_steps=0,
            strategy=strategy,
            precision=self.precision,
        )
        trainer.fit(model, datamodule)
        trainer.test(ckpt_path="best", dataloaders=datamodule.val_dataloader())

        wandb.finish()
        self._append_logger_name(cp_name, run.name)
        return f"{cp_name}{self.extension}"
