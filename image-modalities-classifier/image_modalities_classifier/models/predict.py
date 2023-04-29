""" Module for predicting modalities """

from typing import List, Dict
from dataclasses import dataclass, field
from torch.cuda import empty_cache

# pylint cannot find max inside torch for some reason
# pylint: disable=no-name-in-module
from torch import no_grad, max as torch_max
from torch.utils.data import DataLoader
import torch.nn.functional as nnf
from numpy import ndarray, hstack, vstack
from pandas import DataFrame
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm
from image_modalities_classifier.dataset.transforms import ModalityTransforms
from image_modalities_classifier.dataset.image_dataset import EvalImageDataset
from image_modalities_classifier.models.modality_module import ModalityModule


@dataclass
class RunConfig:
    """Store config data for execution"""

    batch_size: int
    num_workers: int
    device: str = field(default="cuda:0")


class SingleModalityPredictor:
    """Instantiates a trained model to predict a modality for a single classifier"""

    def __init__(self, model_path: str, config: RunConfig):
        # checkpoint = torch.load(model_path)
        self.module = ModalityModule.load_from_checkpoint(model_path)
        self.mean = self.module.hparams["mean_dataset"]
        self.std = self.module.hparams["std_dataset"]
        self.classes = self.module.hparams["classes"]
        self.name = self.module.hparams["name"]
        self.config = config

        transforms_manager = ModalityTransforms(self.name, self.mean, self.std)
        self.transforms = transforms_manager.test_transforms()

        self.decoder = LabelEncoder()
        self.decoder.fit(self.classes)
        self.model = self.module.model

        # self.model = EfficientNet(name="efficientnet-b1", num_classes=4)
        # state_dict = {}
        # for key in checkpoint["state_dict"].keys():
        #     if "model.model" in key:
        #         new_key = key[6:]
        #         state_dict[new_key] = checkpoint["state_dict"][key]
        # self.model.load_state_dict(state_dict)

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
            drop_last=False,
        )
        return loader

    def _predict(self, dataloader: DataLoader) -> ndarray:
        """Predict over dataloader and return a list of classes"""
        predictions = []
        with no_grad():
            for batch_imgs in tqdm(dataloader):
                data = batch_imgs.to(self.config.device)
                batch_outputs = self.model(data)
                batch_predictions = batch_outputs.argmax(dim=-1).cpu()
                predictions.append(batch_predictions)
            prediction_stack = hstack(predictions)
            return prediction_stack

    def _predict_with_probs(self, dataloader: DataLoader) -> ndarray:
        """Predict over dataloader and return a list of classes"""
        probabilities = []
        predictions = []
        with no_grad():
            for batch_imgs in tqdm(dataloader):
                data = batch_imgs.to(self.config.device)
                batch_outputs = self.model(data)

                probs = nnf.softmax(batch_outputs, dim=1)
                _, batch_predictions = torch_max(batch_outputs, dim=1)

                probs = probs.cpu().tolist()
                batch_predictions = batch_predictions.cpu().tolist()

                predictions += batch_predictions
                probabilities += probs

            return predictions, probabilities

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
        self.model.eval().to(self.config.device)
        predictions = self._predict(loader)
        if as_classes:
            return self._as_classes(predictions)
        return predictions

    def predict_with_probs(
        self,
        data: DataFrame,
        base_img_dir: str,
        path_col: str = "img_path",
        as_classes: bool = True,
    ) -> List[str]:
        """Predict from input dataframe and also return prediction probabilities"""
        loader = self._get_dataloader(data, base_img_dir, path_col=path_col)
        self.model.eval().to(self.config.device)
        predictions, probabilities = self._predict_with_probs(loader)
        if as_classes:
            return self._as_classes(predictions), probabilities
        return predictions, probabilities

    def features(self, data: DataFrame, base_img_dir: str, path_col: str = "img_path"):
        """Extract features from layer before FC"""
        loader = self._get_dataloader(data, base_img_dir, path_col=path_col)
        feature_extractor = self.model.feature_extractor()
        feature_extractor.to(self.config.device)
        feature_extractor.eval()
        features = []
        with no_grad():
            for batch_imgs in tqdm(loader):
                data = batch_imgs.to(self.config.device)
                batch_features = feature_extractor(data).cpu()
                features.append(batch_features)
        del feature_extractor
        return vstack(features)

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

    def _load_dataframe(self, image_names: List[str]) -> DataFrame:
        """Load a dummy dataframe because the Dataset requires the data to
        be organized in a dataframe.
        The prediction column starts as "" to match the classname of classifier
        at the root (higher-modality), which reflects that the classifier has
        no parent. We prefer "" over None to be able to do
        .loc[df.prediction==CLASSNAME] later, and None requires a isna()
        comparison. Therefore, == is simpler when all are strings.
        """
        data = DataFrame(columns=["img_path"], data=image_names)
        data.loc[:, "prediction"] = ""
        return data

    def _merge_values(self, data: DataFrame, updated_subset: DataFrame) -> DataFrame:
        """merge update dataframes with latest predicted values"""
        data.set_index("img_path", inplace=True)
        data.update(updated_subset.set_index("img_path"))
        return data.reset_index(inplace=True)

    def predict(self, relative_img_paths: List[str], base_img_path: str) -> DataFrame:
        """Traverse the classifiers in BFS to add labels by level"""
        data = self._load_dataframe(relative_img_paths)

        fringe = [self.classifiers]
        while len(fringe) > 0:
            classifier_node = fringe.pop(0)
            class_name = classifier_node["classname"]
            if classifier_node["children"]:
                fringe += classifier_node["children"]

            model = SingleModalityPredictor(classifier_node["path"], self.config)
            filtered_imgs = data.loc[data.prediction == class_name].copy()
            if len(filtered_imgs) > 0:
                predictions = model.predict(
                    filtered_imgs, base_img_path, as_classes=True
                )
                filtered_imgs.loc[:, "prediction"] = predictions
                self._merge_values(data, filtered_imgs)
        return data
