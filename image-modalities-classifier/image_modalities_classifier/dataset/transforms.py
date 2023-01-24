""" Transformation for the Image Modality Classifier """

from torchvision import transforms
from torch import Tensor


class ModalityTransforms:
    """Image transformations during training and inference"""

    def __init__(self, train_mean: Tensor, train_std: Tensor):
        self.mean = train_mean
        self.std = train_std

    @staticmethod
    def basic_transforms() -> transforms.Compose:
        """Basic transformation needed to at least change image into tensor"""
        basics = [
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ]
        return transforms.Compose(basics)

    def train_transforms(self) -> transforms.Compose:
        """Image transformations for the training set"""
        train_transforms = [
            transforms.ToPILImage(),
            transforms.Resize((256, 256)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(15),
            transforms.CenterCrop((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std),
        ]
        return transforms.Compose(train_transforms)

    def val_transforms(self) -> transforms.Compose:
        """Image transformations for the training set"""

        val_transforms = [
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std),
        ]
        return transforms.Compose(val_transforms)

    def test_transforms(self) -> transforms.Compose:
        """Image transformations for the test set"""
        return self.val_transforms()

    def inference_transforms(self) -> transforms.Compose:
        """Image transformations for images in the wild"""
        return self.val_transforms()
