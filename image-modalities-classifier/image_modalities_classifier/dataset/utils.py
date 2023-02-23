"Utilities for the dataset module"

from os import listdir, path, makedirs
from pathlib import Path
from typing import Dict
from pandas import DataFrame
from skimage import io
from skimage.color import gray2rgb
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt


def remove_small_classes(data: DataFrame, col_name: str, threshold: int = 100):
    """Remove class from dataframe if there are less than threshold samples.
    Added to avoid putting classification efforts on classes with very few
    elements.
    """
    grouped_count = data.groupby(col_name)[col_name].count()
    to_remove = []
    for label in grouped_count.index:
        if grouped_count[label] < threshold:
            to_remove.append(label)
    return data[~data.label.isin(to_remove)]


def show_batch_images(route, class_name, rows, cols):
    """Display sample images from folder"""
    images = listdir(path.join(route, class_name))
    row = rows
    col = cols
    plt.figure(figsize=(20, (row / col) * 12))
    plt.suptitle(f"{class_name} images", y=1.05, fontsize=30)
    for j in range(row * col):
        plt.subplot(row, col, j + 1)
        img = path.join(route, class_name, images[j])
        img = io.imread(img)
        if len(img.shape) == 2:
            img = gray2rgb(img)
        else:
            img = img[:, :, :3]
        plt.imshow(img)
        plt.title(f"Image {class_name}")
    plt.tight_layout()
    plt.show()


def df_from_disk_no_captions(
    base_dir: str, rel_dir: str, label: str, original: str, source: str
):
    """Load images in dataframe and assign the same label"""
    dir_path = Path(base_dir) / rel_dir
    img_names = [
        x
        for x in listdir(dir_path)
        if x.lower().endswith((".jpg", ".png", ".jpeg", ".bmp")) and "gradcam" not in x
    ]
    widths = []
    heights = []

    for img_name in img_names:
        img = Image.open(dir_path / img_name)
        width, height = img.size
        widths.append(width)
        heights.append(height)
    img_paths = [str(Path(rel_dir) / x) for x in img_names]
    dframe = DataFrame(
        list(zip(img_names, img_paths, widths, heights)),
        columns=["img", "img_path", "width", "height"],
    )
    dframe["label"] = label
    dframe["source"] = source
    dframe["caption"] = ""
    dframe["is_gt"] = True
    dframe["original"] = original
    return dframe


def df_from_disk_with_mapper(
    base_dir: str, rel_dir: str, mapper: Dict, source: str, captions_df: DataFrame
):
    """Load images from directory where subdirectories group classes, and use
    mapper to get the expected modality"""
    dir_path = Path(base_dir) / rel_dir
    classes = [elem for elem in listdir(dir_path) if Path(dir_path / elem).is_dir()]

    all_img_names = []
    widths = []
    heights = []
    captions = []
    labels = []
    originals = []
    img_paths = []

    for label_cat in classes:
        if label_cat not in mapper:
            continue
        img_names = [
            x
            for x in listdir(dir_path / label_cat)
            if x.lower().endswith((".jpg", ".png", ".jpeg", ".bmp"))
            and "gradcam" not in x
        ]
        all_img_names += img_names

        for img_name in img_names:
            img = Image.open(dir_path / label_cat / img_name)
            width, height = img.size
            widths.append(width)
            heights.append(height)
            caption = ""
            try:
                caption = captions_df.loc[img_name].caption
            except KeyError:
                # print(f"{img_name} not found in captions")
                pass
            captions.append(caption)
            labels.append(mapper[label_cat])
            originals.append(label_cat)
            img_paths.append(str(Path(rel_dir) / label_cat / img_name))

    dframe = DataFrame(
        list(
            zip(all_img_names, img_paths, widths, heights, labels, originals, captions)
        ),
        columns=["img", "img_path", "width", "height", "label", "original", "caption"],
    )
    dframe["source"] = source
    dframe["is_gt"] = True
    return dframe


def resize_img_and_save(input_img_path: str, output_folder: str, max_size: int) -> None:
    """Resize input image proportionally based on max size and save output
    image in output_folder in JPEG format
    """
    img_path = Path(input_img_path)
    img = Image.open(img_path)
    width, height = img.size

    out_fig_path = Path(output_folder) / f"{img_path.stem}.jpg"
    if width > max_size or height > max_size:
        ratio = min(max_size / width, max_size / height)
        new_width = width * ratio
        new_height = height * ratio
        img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

    img = img.convert("RGB")
    img.save(out_fig_path, "JPEG")


def scale_dataset(input_path: str, output_path: str, max_size: int) -> None:
    """Scale the images in the dataset because figures from publications are not
    that big. This method does not check recursively inside folders in input_path.
    """
    input_dataset_path = Path(input_path)
    output_dataset_path = Path(output_path)

    if not input_dataset_path.exists():
        raise FileNotFoundError(input_path)
    if not output_dataset_path.exists():
        makedirs(output_dataset_path)

    img_names = [
        el
        for el in listdir(input_dataset_path)
        if el.lower().endswith((".jpg", ".png", ".jpeg", ".bmp"))
        and "gradcam" not in el
    ]
    for img_name in tqdm(img_names):
        resize_img_and_save(
            str(input_dataset_path / img_name),
            str(output_dataset_path),
            max_size=max_size,
        )
