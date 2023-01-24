""" Module for predicting modalities """

from typing import List
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.preprocessing import LabelEncoder
from image_modalities_classifier.dataset.transforms import ModalityTransforms
from image_modalities_classifier.dataset.image_dataset import EvalImageDataset
from image_modalities_classifier.models.resnet import Resnet


# TODO: this should be inside the model data (hparams)
MODALITY_CLASSES = {
    "higher-modality": [],
    "molecular": ["mol.3ds", "mol.che", "mol.dna", "mol.pro"],
    "microscopy": ["mic.ele", "mic.flu", "mic.lig"],
    "graphics": [
        "gra.3dr",
        "gra.flow",
        "gra.his",
        "gra.lin",
        "gra.oth",
        "gra.sca",
        "gra.sig",
    ],
    "radiology": ["rad.ang", "rad.cmp", "rad.uls", "rad.oth", "rad.xra"],
    "experimental": ["exp.gel", "exp.pla"],
}


@dataclass
class RunConfig:
    """Store config data for execution"""

    batch_size: int
    num_workers: int
    device: str = field(default="cuda:0")


class SingleModalityPredictor:
    """Instantiates a trained model to predict a modality for a single classifier"""

    def __init__(self, name: str, model_path: str, config: RunConfig):
        self.name = name
        self.model = Resnet.load_from_checkpoint(model_path)
        self.mean = self.model.hparams["mean_dataset"]
        self.std = self.model.hparams["mean_dataset"]
        self.config = config

        transforms_manager = ModalityTransforms(self.mean, self.std)
        self.transforms = transforms_manager.test_transforms()

        self.decoder = LabelEncoder()
        self.decoder.fit(MODALITY_CLASSES[self.name])

    def _get_dataloader(self, data: pd.DataFrame, base_img_dir: str) -> DataLoader:
        """Loads data into dataloader for prediction"""
        dataset = EvalImageDataset(data, base_img_dir, self.transforms, path_col="path")
        loader = DataLoader(
            dataset=dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
        )
        return loader

    def _predict(self, dataloader: DataLoader) -> List[str]:
        """Predict over dataloader and return a list of classes"""
        self.model.eval()
        predictions = []
        with torch.no_grad():
            for batch_imgs in dataloader:
                data = batch_imgs.to(self.config.device)
                batch_outputs = self.model(data)
                _, batch_predictions = torch.max(batch_outputs, dim=1)
                batch_predictions = batch_predictions.cpu()
                predictions.append(predictions)
            prediction_stack = np.hstack(predictions)
            return self.decoder.inverse_transform(prediction_stack)

    def predict(self, data: pd.DataFrame, base_img_dir: str) -> List[str]:
        """Predict from input dataframe"""
        loader = self._get_dataloader(data, base_img_dir)
        self.model.to(self.config.device)
        return self._predict(loader)

    def free(self):
        """Remove model from gpu"""
        del self.model
