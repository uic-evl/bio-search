""" Transformation for the Image Modality Classifier """

from torchvision import transforms
from torch import Tensor

input_sizes = {
    "resnet18": {"resize": 256, "crop": 224},
    "resnet34": {"resize": 256, "crop": 224},
    "resnet50": {"resize": 256, "crop": 224},
    "resnet101": {"resize": 256, "crop": 224},
    "resnet152": {"resize": 256, "crop": 224},
    "efficientnet-b0": {"resize": 256, "crop": 224},
    "efficientnet-b1": {"resize": 272, "crop": 240},
    "efficientnet-b4": {"resize": 412, "crop": 380},
    "efficientnet-b5": {"resize": 482, "crop": 456},
}


class ModalityTransforms:
    """Image transformations during training and inference"""

    def __init__(self, model_name: str, train_mean: Tensor, train_std: Tensor):
        self.model_name = model_name
        self.mean = train_mean
        self.std = train_std
        self.resize_size = input_sizes[self.model_name]["resize"]
        self.crop_size = input_sizes[self.model_name]["crop"]

    @staticmethod
    def basic_transforms(model_name: str = "resnet18") -> transforms.Compose:
        """Basic transformation needed to at least change image into tensor"""
        image_size = input_sizes[model_name]["crop"]
        basics = [
            transforms.ToPILImage(),
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
        ]
        return transforms.Compose(basics)

    def train_transforms(self) -> transforms.Compose:
        """Image transformations for the training set"""
        train_transforms = [
            transforms.ToPILImage(),
            transforms.Resize((self.resize_size, self.resize_size)),
            transforms.RandomHorizontalFlip(p=0.2),
            # transforms.RandomRotation(15),
            transforms.CenterCrop((self.crop_size, self.crop_size)),
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std),
        ]
        return transforms.Compose(train_transforms)

    def val_transforms(self) -> transforms.Compose:
        """Image transformations for the training set"""

        val_transforms = [
            transforms.ToPILImage(),
            transforms.Resize((self.resize_size, self.resize_size)),
            transforms.CenterCrop((self.crop_size, self.crop_size)),
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
