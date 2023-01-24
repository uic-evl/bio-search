""" Test datasets and data modules"""

from os import listdir
from pathlib import Path
import pandas as pd
import torch
from numpy import int64
from image_modalities_classifier.dataset.image_dataset import ImageDataset
from image_modalities_classifier.dataset.transforms import ModalityTransforms


def test_image_dataset():
    """Test that  the image dataset returns pair of image, label values"""
    path_col = "img_path"
    label_col = "label"

    base_img_dir = str(Path("./tests/sample_data").resolve())
    img_paths = [x for x in listdir(base_img_dir) if x.endswith(".png")]
    labels = [1] * len(img_paths)
    input_df = pd.DataFrame(zip(img_paths, labels), columns=[path_col, label_col])

    transforms = ModalityTransforms.basic_transforms()
    dataset = ImageDataset(input_df, base_img_dir, transforms, path_col, label_col)

    image, label = dataset[0]
    assert isinstance(image, torch.Tensor)
    assert list(image.shape) == [3, 224, 224]
    assert isinstance(label, int64)
    assert label == 1
