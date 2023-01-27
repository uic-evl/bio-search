""" Datasets for training, validation, test, and inference """

from pathlib import Path
from typing import Optional, Tuple
import torch
from pandas import DataFrame
from skimage import io
from skimage.color import gray2rgb
from torchvision.transforms import Compose
from numpy import int64


def read_image(data: DataFrame, base_dir: str, path_col: str, idx):
    """Convert image in index to RGB"""
    img_path = base_dir / data.iloc[idx][path_col]
    image = io.imread(img_path, pilmode="RGB")
    # some clef images were grayscale
    if len(image.shape) == 2:
        image = gray2rgb(image)
    else:
        image = image[:, :, :3]
    return image


class ImageDataset(torch.utils.data.Dataset):
    """Dataset for training, validation and testing steps that returns
    image and label tuples. It assumes that the input dataframe already has
    a column processed by a label encoder (i.e., a int column exists indicating
    the classes)
    """

    def __init__(
        self,
        data: DataFrame,
        base_img_dir: str,
        transforms: Optional[Compose],
        path_col: str = "img_path",
        label_col: str = "label",
    ):
        self.data = data
        self.base_dir = Path(base_img_dir)
        self.transforms = transforms
        self.label_col = label_col
        self.path_col = path_col

    def __len__(self) -> int:
        return self.data.shape[0]

    def __getitem__(self, idx) -> Tuple[torch.Tensor, int64]:
        if torch.is_tensor(idx):
            idx = idx.tolist()

        image = read_image(self.data, self.base_dir, self.path_col, idx)
        labels = self.data.iloc[idx][self.label_col]

        if self.transforms:
            image = self.transforms(image)
        return (image, labels)


class EvalImageDataset(torch.utils.data.Dataset):
    """Dataset used for inference.
    Compared to the ImageDataset, this dataset does not have any label value,
    so it only cares about converting the images based on the transform, and
    returning the tensors
    """

    def __init__(
        self,
        data: DataFrame,
        base_img_dir: str,
        image_transform=None,
        path_col="img_path",
    ):
        self.base_dir = Path(base_img_dir)
        self.image_transform = image_transform
        self.path_col = path_col
        self.data = data

    def __len__(self) -> int:
        return self.data.shape[0]

    def __getitem__(self, idx) -> torch.Tensor:
        if torch.is_tensor(idx):
            idx = idx.tolist()
        image = read_image(self.data, self.base_dir, self.path_col, idx)
        if self.image_transform:
            image = self.image_transform(image)
        return image
