"""Define data modules for image modality classification"""

from pathlib import Path
import pytorch_lightning as pl
from pytorch_lightning import seed_everything
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import class_weight
from torch.utils.data import DataLoader


from image_modalities_classifier.dataset.image_dataset import ImageDataset
from image_modalities_classifier.dataset.transforms import ModalityTransforms


ENCODED_LABEL_COL = "enc_label"


class ImageDataModule(pl.LightningDataModule):
    """Responsible for preparing the data and providing the dataloaders for
    train, validation and test"""

    def __init__(
        self,
        model_name: str,
        label_encoder: LabelEncoder,
        batch_size: int,
        data_path: str,
        base_img_dir: str,
        train_mean: float,
        train_std: float,
        seed: int = 42,
        num_workers: int = 8,
        partition_col: str = "split_set",
        label_col: str = "label",
        path_col: str = "img_path",
        remove_small=True,
    ):
        super().__init__()
        self.data = None
        self.data_path = data_path
        self.remove_small = remove_small
        self.label_encoder = label_encoder
        self.base_img_dir = base_img_dir

        self.batch_size = batch_size
        self.num_workers = num_workers
        self.seed = seed

        self.class_weights = None
        self.partition_col = partition_col
        self.label_col = label_col
        self.path_col = path_col

        self.transforms = ModalityTransforms(model_name, train_mean, train_std)

    def prepare_data(self):
        path = Path(self.data_path)
        if path.suffix.lower() == ".csv":
            self.data = pd.read_csv(self.data_path, sep="\t")
        else:
            self.data = pd.read_parquet(self.data_path)

        # create new column with encoded values
        self.data[ENCODED_LABEL_COL] = self.label_encoder.transform(
            self.data[self.label_col].values
        )

    def set_seed(self):
        """Pytorch Lightning seed everything"""
        seed_everything(self.seed)

    # pylint: disable=arguments-differ
    def setup(self, stage: str):
        train_df = self.data[self.data[self.partition_col] == "TRAIN"]
        y_train = train_df[self.label_col].values
        self.class_weights = class_weight.compute_class_weight(
            "balanced", classes=np.unique(y_train), y=y_train
        )
        del train_df, y_train

    def train_dataloader(self):
        train_df = self.data[self.data[self.partition_col] == "TRAIN"]

        train_dataset = ImageDataset(
            data=train_df,
            base_img_dir=self.base_img_dir,
            transforms=self.transforms.train_transforms(),
            label_col=ENCODED_LABEL_COL,
            path_col=self.path_col,
        )

        return DataLoader(
            dataset=train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
        )

    def val_dataloader(self):
        val_df = self.data[self.data[self.partition_col] == "VAL"]

        val_dataset = ImageDataset(
            data=val_df,
            base_img_dir=self.base_img_dir,
            transforms=self.transforms.val_transforms(),
            label_col=ENCODED_LABEL_COL,
            path_col=self.path_col,
        )

        return DataLoader(
            dataset=val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )

    def test_dataloader(self):
        test_df = self.data[self.data[self.partition_col] == "TEST"]

        test_dataset = ImageDataset(
            data=test_df,
            base_img_dir=self.base_img_dir,
            transforms=self.transforms.test_transforms(),
            label_col=ENCODED_LABEL_COL,
            path_col=self.path_col,
        )

        return DataLoader(
            dataset=test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )
