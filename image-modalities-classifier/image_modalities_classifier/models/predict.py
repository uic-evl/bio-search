""" Module for predicting modalities """

from typing import List, Dict
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


class ModalityPredictor:
    """Predicts modalities by traversing over a tree of classifiers
    Parameters:
    -----------
    classifiers: dict
        Dictionary with structure
        { 'classifier': str, # full name of the classifier
          'classname': str,  # short-name defined as the labels (e.g., exp)
          'path': str,
          'children': [
            {... recursive definition }
          ]
        }
    """

    def __init__(self, classifiers: Dict, config: RunConfig):
        self.classifiers = classifiers
        self.config = config
        self.data = None

    def _load_dataframe(self, image_names: List[str]) -> DataFrame:
        """Load a dummy dataframe because the Dataset requires the data to
        be organized in a dataframe.
        """
        self.data = DataFrame(columns=["img_path"], data=image_names)
        self.data["prediction"] = None

    def _merge_values(self, updated_subset: DataFrame) -> DataFrame:
        """merge update dataframes with latest predicted values"""
        self.data.set_index("img_path", inplace=True)
        self.data.update(updated_subset.set_index("img_path"))
        self.data.reset_index()

    def predict(self, relative_img_paths: List[str], base_img_path: str) -> DataFrame:
        """Traverse the classifiers in BFS to add labels by level"""
        self._load_dataframe(relative_img_paths)

        fringe = [self.classifiers]
        while len(fringe) > 0:
            classifier_node = fringe.pop(0)
            class_name = classifier_node["classname"]
            if classifier_node["children"]:
                fringe += classifier_node["children"]

            model = SingleModalityPredictor(classifier_node["path"], self.config)
            filtered_imgs = self.data.loc[self.data.prediction == class_name]
            predictions = model.predict(filtered_imgs, base_img_path, as_classes=True)
            filtered_imgs["prediction"] = predictions

            self._merge_values(filtered_imgs)
