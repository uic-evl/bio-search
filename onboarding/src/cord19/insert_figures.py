from figure import (
    get_full_labels,
    load_images_from_external_sources,
    calc_img_path_length,
    is_figure,
    get_parent_image,
    build_pmc_to_id_doc_dic,
    load_figures_from_cord19,
    get_map_fig_uri_2_db_id,
    get_coordinate_mapping,
    build_tinman_doc_mapping,
    insert_labels,
    load_images_from_tinman,
    insert_figures,
)

from pathlib import Path
from dotenv import dotenv_values
from PIL import Image
import pandas as pd

STATUS_LABELED = 0
STATUS_UNLABELED = 1
STATUS_LABELED_EXTERNALLY = 2

TYPE_FIGURE = 0
TYPE_SUBFIGURE = 1


def insert_external_images(config: dict, df: pd.DataFrame, full_labels: dict):
    print("inserting figures from external sources")
    figures = load_images_from_external_sources(df, full_labels)
    insert_figures(config, figures)


def insert_cord19_images(config: dict, df: pd.DataFrame, base_path: str):
    # the main issue with these data is that we have figures and subfigures
    # so we estimate the relationship based on the image path
    df["path_length"] = df.apply(lambda x: calc_img_path_length(x.img_path), axis=1)
    df["type"] = df.apply(lambda x: is_figure(x.path_length), axis=1)
    df["parent_id"] = df.apply(lambda x: get_parent_image(x.img_path, x.type), axis=1)

    # then we need to identify the parent document in the database
    pmc2docid_dict = build_pmc_to_id_doc_dic(config)

    # insert figures first so we can query the figure_id later
    df_figures = df[df.type == TYPE_FIGURE]
    df_figures["coordinates"] = None
    figures = load_figures_from_cord19(df_figures, pmc2docid_dict)
    print("inserting figures for cord19")
    insert_figures(config, figures)

    # now gather the ids to link figures and subfigures
    img_path_2_id = get_map_fig_uri_2_db_id(config)
    df_subfigures = df[df.type == TYPE_SUBFIGURE]
    coordinate_mapping = get_coordinate_mapping(df_subfigures, Path(base_path))
    df_subfigures.parent_id = df_subfigures.apply(
        lambda x: img_path_2_id[x.parent_id], axis=1
    )
    df_subfigures["coordinates"] = df_subfigures.apply(
        lambda x: coordinate_mapping.get(x.img_path, None), axis=1
    )
    print("inserting subfigures for cord19")
    figures = load_figures_from_cord19(df_subfigures, pmc2docid_dict)
    insert_figures(config, figures)


def insert_tinman_figures(
    config: dict, df: pd.DataFrame, full_labels: dict, base_path: Path
):
    # the first subfolder may be the key to join documents and images
    mapping_docs = build_tinman_doc_mapping(config)

    # the tinman collection has only subfigures, but we can query the
    # figures as they are also in the existing folders
    tinman_figures = {}
    for _, row in df.iterrows():
        figure_path = f"{Path(row.img_path).parent}.jpg"
        w, h = Image.open(base_path / figure_path).size
        if figure_path not in tinman_figures:
            tinman_figures[figure_path] = {
                "img": figure_path.split("/")[-1],
                "source": "tinman",
                "type": TYPE_FIGURE,
                "img_path": figure_path,
                "label": None,
                "split_set": None,
                "features": None,
                "prediction": None,
                "width": w,
                "height": h,
                "caption": row.caption,
                "ms_metric": None,
                "en_metric": None,
                "pred_probs": None,
                "parent_id": None,
            }

    tinman_figures = [tinman_figures[x] for x in tinman_figures]
    df_tinman_figures = pd.DataFrame(tinman_figures)
    df_tinman_figures["coordinates"] = None
    df_tinman_figures["parent_folder"] = df_tinman_figures.apply(
        lambda x: x.img_path.split("/")[1], axis=1
    )
    df_tinman_figures["doc_id"] = df_tinman_figures.apply(
        lambda x: mapping_docs[x.parent_folder], axis=1
    )
    figures = load_images_from_tinman(df_tinman_figures, full_labels)
    print("inserting figures from tinman")
    insert_figures(config, figures)

    # now match figures and subfigures
    img_path_2_id = get_map_fig_uri_2_db_id(config)
    df["parent_id"] = df.apply(
        lambda x: get_parent_image(x.img_path, TYPE_SUBFIGURE), axis=1
    )
    df.parent_id = df.apply(lambda x: img_path_2_id[x.parent_id], axis=1)

    df["parent_folder"] = df.apply(lambda x: x.img_path.split("/")[1], axis=1)
    df["doc_id"] = df.apply(lambda x: mapping_docs[x.parent_folder], axis=1)
    df["type"] = TYPE_SUBFIGURE
    coordinate_mapping = get_coordinate_mapping(df, Path(base_path))
    df["coordinates"] = df.apply(
        lambda x: coordinate_mapping.get(x.img_path, None), axis=1
    )

    subfigures = load_images_from_tinman(df, full_labels)
    print("inserting subfigures from tinman")
    insert_figures(config, subfigures)


if __name__ == "__main__":
    env_file = "../../.env"
    config = dotenv_values(env_file)
    root = Path("/Users/jtrell2/data/biocuration/")

    vil_files_path = root / "vil-al-interface/files/cord19"
    all_path = vil_files_path / "all.parquet"

    df_all = pd.read_parquet(all_path)

    higher_mod_parquet_file = "cord19_higher-modality_v1.parquet"
    tax_parquet_files = [
        "cord19_experimental_v1.parquet",
        "cord19_gel_v1.parquet",
        "cord19_graphics_v1.parquet",
        "cord19_microscopy_v1.parquet",
        "cord19_molecular_v1.parquet",
        "cord19_radiology_v1.parquet",
        "cord19_electron_v1.parquet",
    ]

    df_all_images = pd.read_parquet(vil_files_path / higher_mod_parquet_file)
    # while exploring radiology images, I found some cases that were not in high modality.parquet
    # this is a mistake, so we need to fusion these images with the full_parquet data
    df_missing_from_full = pd.read_parquet("./missing_rad_ang.parquet")
    df_all_images = pd.concat([df_all_images, df_missing_from_full])

    df_tinman = df_all_images[df_all_images.source == "tinman"]
    df_cord19 = df_all_images[df_all_images.source == "cord19"]
    df_others = df_all_images[~df_all_images.source.isin(["tinman", "cord19"])]

    df_full_labels = pd.read_parquet(vil_files_path / "all.parquet")
    df_full_labels = pd.concat([df_full_labels, df_missing_from_full])

    high_modality_filename = "cord19_higher-modality_v1.parquet"
    children_filenames = tax_parquet_files.copy()
    children_filenames.append(high_modality_filename)
    parquet_files = [vil_files_path / x for x in children_filenames]

    full_labels = get_full_labels(df_full_labels)
    # insert document from external sources that do not have a relationship
    # with any document
    insert_external_images(config, df_others, full_labels)
    # then images that do have relationship with documents
    insert_cord19_images(config, df_cord19, str(root))
    insert_tinman_figures(config, df_tinman, full_labels, root)
    # inserting existing labels, predictions and features
    insert_labels(config, parquet_files)
