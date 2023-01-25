""" Module for predicting modalities """

from typing import List
from dataclasses import dataclass, field
from torch.cuda import empty_cache

# pylint cannot find max inside torch for some reason
# pylint: disable=no-name-in-module
from torch import no_grad, max as torch_max
from torch.utils.data import DataLoader
from numpy import ndarray, hstack
from pandas import DataFrame
from sklearn.preprocessing import LabelEncoder
from image_modalities_classifier.dataset.transforms import ModalityTransforms
from image_modalities_classifier.dataset.image_dataset import EvalImageDataset
from image_modalities_classifier.models.resnet import Resnet


@dataclass
class RunConfig:
    """Store config data for execution"""

    batch_size: int
    num_workers: int
    device: str = field(default="cuda:0")


class SingleModalityPredictor:
    """Instantiates a trained model to predict a modality for a single classifier"""

    def __init__(self, model_path: str, config: RunConfig):
        self.model = Resnet.load_from_checkpoint(model_path)
        self.mean = self.model.hparams["mean_dataset"]
        self.std = self.model.hparams["mean_dataset"]
        self.classes = self.model.hparams["classes"]
        self.config = config

        transforms_manager = ModalityTransforms(self.mean, self.std)
        self.transforms = transforms_manager.test_transforms()

        self.decoder = LabelEncoder()
        self.decoder.fit(self.classes)

    def _get_dataloader(
        self, data: DataFrame, base_img_dir: str, path_col: str
    ) -> DataLoader:
        """Loads data into dataloader for prediction"""
        dataset = EvalImageDataset(
            data, base_img_dir, self.transforms, path_col=path_col
        )
        loader = DataLoader(
            dataset=dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
        )
        return loader

    def _predict(self, dataloader: DataLoader) -> ndarray:
        """Predict over dataloader and return a list of classes"""
        self.model.eval()
        predictions = []
        with no_grad():
            for batch_imgs in dataloader:
                data = batch_imgs.to(self.config.device)
                batch_outputs = self.model(data)
                _, batch_predictions = torch_max(batch_outputs, dim=1)
                batch_predictions = batch_predictions.cpu()
                predictions.append(batch_predictions)
            prediction_stack = hstack(predictions)
            return prediction_stack

    def _as_classes(self, predictions) -> List[str]:
        return self.decoder.inverse_transform(predictions)

    def predict(
        self,
        data: DataFrame,
        base_img_dir: str,
        path_col: str = "img_path",
        as_classes: bool = True,
    ) -> List[str]:
        """Predict from input dataframe"""
        loader = self._get_dataloader(data, base_img_dir, path_col=path_col)
        self.model.to(self.config.device)
        predictions = self._predict(loader)
        if as_classes:
            return self._as_classes(predictions)
        return predictions

    def free(self):
        """Remove model from gpu"""
        del self.model
        empty_cache()
