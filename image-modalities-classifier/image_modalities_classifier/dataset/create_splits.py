""" Script to create the TRAIN/VAL/TEST sets for each classifier.
Outputs are saved in the data folder 
"""

from typing import List
from os import listdir, makedirs
from pathlib import Path
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit

RANDOM_STATE = 43
INPUT_PARQUETS = "_raw_parquets_smaller"

splits_by_classifier = {
    "gel": {"test": 0.1, "val": 0.1},
    "experimental": {"test": 0.1, "val": 0.1},
    "electron": {"test": 0.1, "val": 0.1},
    "microscopy": {"test": 0.1, "val": 0.1},
    "graphics": {"test": 0.025, "val": 0.025},
    "radiology": {"test": 0.025, "val": 0.025},
    "molecular": {"test": 0.1, "val": 0.1},
    "photography": {"test": 0.1, "val": 0.1},
    "higher-modality": {"test": 0.05, "val": 0.05},
}


def split_sets(
    data: pd.DataFrame,
    labels: List[str],
    test_size: float = 0.2,
    val_size: float = 0.1,
    random_state: int = 42,
):
    """Split by label"""
    df_set = data[data.label.isin(labels)].reset_index()
    y = df_set.label
    sss = StratifiedShuffleSplit(
        n_splits=5, test_size=test_size, random_state=random_state
    )
    for _, (train_index, test_index) in enumerate(sss.split(df_set, y)):
        df_set.loc[test_index, "split_set"] = "TEST"
        df_set.loc[train_index, "split_set"] = "TRAIN"

    df_test = df_set[df_set.split_set == "TEST"].reset_index()
    df_train = df_set[df_set.split_set == "TRAIN"].reset_index()
    y_train = df_train.label

    # split for validation
    num_val = int(df_set.shape[0] * val_size)
    val_test_size = num_val / df_train.shape[0]

    sss = StratifiedShuffleSplit(
        n_splits=5, test_size=val_test_size, random_state=random_state
    )
    for _, (train_index, test_index) in enumerate(sss.split(df_train, y_train)):
        df_train.loc[test_index, "split_set"] = "VAL"
        df_train.loc[train_index, "split_set"] = "TRAIN"

    df_val = df_train[df_train.split_set == "VAL"]
    df_train = df_train[df_train.split_set == "TRAIN"]

    return pd.concat([df_train, df_val, df_test]).reset_index(drop=True)


def split_sets_multistratified(
    data: pd.DataFrame,
    labels: List[str],
    test_size: float = 0.2,
    val_size: float = 0.1,
    random_state: int = 42,
):
    """Split by source and label"""
    df_set = data[data.label.isin(labels)].reset_index()

    mskf = MultilabelStratifiedShuffleSplit(
        n_splits=5, test_size=test_size, random_state=random_state
    )
    for _, (train_index, test_index) in enumerate(
        mskf.split(df_set, df_set[["label", "source"]])
    ):
        df_set.loc[test_index, "split_set"] = "TEST"
        df_set.loc[train_index, "split_set"] = "TRAIN"

    df_test = df_set[df_set.split_set == "TEST"].reset_index()
    df_train = df_set[df_set.split_set == "TRAIN"].reset_index()

    # split for validation
    num_val = int(df_set.shape[0] * val_size)
    val_test_size = num_val / df_train.shape[0]

    mskf = MultilabelStratifiedShuffleSplit(
        n_splits=5, test_size=val_test_size, random_state=random_state
    )
    for _, (train_index, test_index) in enumerate(
        mskf.split(df_train, df_train[["label", "source"]])
    ):
        df_train.loc[test_index, "split_set"] = "VAL"
        df_train.loc[train_index, "split_set"] = "TRAIN"

    df_val = df_train[df_train.split_set == "VAL"]
    df_train = df_train[df_train.split_set == "TRAIN"]

    return pd.concat([df_train, df_val, df_test]).reset_index(drop=True)


def create_output_folder(base_folder: str) -> str:
    """create a numbered folder to save parquet files"""
    folders = [
        el
        for el in listdir(base_folder)
        if (Path(base_folder) / el).is_dir() and el.isdigit()
    ]
    if len(folders) == 0:
        output_name = 0
    else:
        folders.sort(reverse=True)
        output_name = int(folders[0]) + 1
    output_path = Path(base_folder) / str(output_name)
    makedirs(output_path)
    return str(output_path)


def add_children(parent_df: pd.DataFrame, child_df: pd.DataFrame, label: str):
    """Concat children and assign parent's label"""
    df_temp = child_df.copy()
    df_temp.label = label
    return pd.concat([parent_df, df_temp]).reset_index(drop=True)


def main():
    """Create folder and save splitted parquet files"""
    data_folder = "./data"

    raw_parquets_path = Path(data_folder).resolve() / INPUT_PARQUETS
    parquet_files = [
        x
        for x in listdir(raw_parquets_path)
        if x.endswith(".parquet") and "captions" not in x
    ]

    df_all = None
    for parquet_file in parquet_files:
        df_local = pd.read_parquet(raw_parquets_path / parquet_file)
        df_all = pd.concat([df_all, df_local])

    # there are only two sources with electron other, better move up one level
    df_all.loc[
        (df_all.source == "tinman") & (df_all.label == "mic.ele.oth"), "label"
    ] = "mic.ele"
    df_all.loc[(df_all.label == "exp.gel.oth"), "label"] = "exp.gel"

    output_folder = create_output_folder(data_folder)

    # split classifiers
    classifier_name = "gel"
    print(classifier_name)
    df_gel = split_sets(
        df_all,
        ["exp.gel.nor", "exp.gel.rpc", "exp.gel.wes"],
        test_size=splits_by_classifier[classifier_name]["test"],
        val_size=splits_by_classifier[classifier_name]["val"],
        random_state=RANDOM_STATE,
    )

    classifier_name = "experimental"
    print(classifier_name)
    df_exp = split_sets(
        df_all,
        ["exp.gel", "exp.pla"],
        test_size=splits_by_classifier[classifier_name]["test"],
        val_size=splits_by_classifier[classifier_name]["val"],
        random_state=RANDOM_STATE,
    )
    df_exp = add_children(df_exp, df_gel, "exp.gel")

    classifier_name = "electron"
    print(classifier_name)
    df_electron = split_sets(
        df_all,
        ["mic.ele.sca", "mic.ele.tra"],
        test_size=splits_by_classifier[classifier_name]["test"],
        val_size=splits_by_classifier[classifier_name]["val"],
        random_state=RANDOM_STATE,
    )

    classifier_name = "microscopy"
    print(classifier_name)
    df_microscopy = split_sets(
        df_all,
        ["mic.ele", "mic.flu", "mic.lig"],
        test_size=splits_by_classifier[classifier_name]["test"],
        val_size=splits_by_classifier[classifier_name]["val"],
        random_state=RANDOM_STATE,
    )
    df_microscopy = add_children(df_microscopy, df_electron, "mic.ele")

    # graphics classifier
    classifier_name = "graphics"
    print(classifier_name)
    df_graphics = split_sets_multistratified(
        df_all,
        ["gra.3dr", "gra.flow", "gra.his", "gra.lin", "gra.sca", "gra.oth", "gra.sig"],
        test_size=splits_by_classifier[classifier_name]["test"],
        val_size=splits_by_classifier[classifier_name]["val"],
        random_state=RANDOM_STATE,
    )

    classifier_name = "radiology"
    print(classifier_name)
    df_radiology = split_sets_multistratified(
        df_all,
        ["rad.cmp", "rad.uls", "rad.xra", "rad.ang"],
        test_size=splits_by_classifier[classifier_name]["test"],
        val_size=splits_by_classifier[classifier_name]["val"],
        random_state=RANDOM_STATE,
    )

    classifier_name = "molecular"
    print(classifier_name)
    df_molecular = split_sets(
        df_all,
        ["mol.3ds", "mol.che", "mol.dna", "mol.pro"],
        test_size=splits_by_classifier[classifier_name]["test"],
        val_size=splits_by_classifier[classifier_name]["val"],
        random_state=RANDOM_STATE,
    )

    classifier_name = "photography"
    print(classifier_name)
    df_photo = split_sets(
        df_all,
        ["pho.der", "pho.org"],
        test_size=splits_by_classifier[classifier_name]["test"],
        val_size=splits_by_classifier[classifier_name]["val"],
        random_state=RANDOM_STATE,
    )

    classifier_name = "higher-modality"
    print(classifier_name)
    df_high_modality = split_sets(
        df_all,
        ["exp", "mic", "gra", "rad", "mol", "pho", "oth"],
        test_size=splits_by_classifier[classifier_name]["test"],
        val_size=splits_by_classifier[classifier_name]["val"],
        random_state=RANDOM_STATE,
    )
    df_high_modality = add_children(df_high_modality, df_exp, "exp")
    df_high_modality = add_children(df_high_modality, df_microscopy, "mic")
    df_high_modality = add_children(df_high_modality, df_graphics, "gra")
    df_high_modality = add_children(df_high_modality, df_radiology, "rad")
    df_high_modality = add_children(df_high_modality, df_molecular, "mol")
    df_high_modality = add_children(df_high_modality, df_photo, "pho")

    # drop extra columns from merge
    cols_to_drop = ["level_0", "index"]
    df_gel.drop(cols_to_drop, axis=1, inplace=True)
    df_exp.drop(cols_to_drop, axis=1, inplace=True)
    df_electron.drop(cols_to_drop, axis=1, inplace=True)
    df_microscopy.drop(cols_to_drop, axis=1, inplace=True)
    df_graphics.drop(cols_to_drop, axis=1, inplace=True)
    df_molecular.drop(cols_to_drop, axis=1, inplace=True)
    df_photo.drop(cols_to_drop, axis=1, inplace=True)
    df_radiology.drop(cols_to_drop, axis=1, inplace=True)
    df_high_modality.drop(cols_to_drop, axis=1, inplace=True)

    df_gel.to_parquet(Path(output_folder) / "cord19_gel_v1.parquet")
    df_exp.to_parquet(Path(output_folder) / "cord19_experimental_v1.parquet")
    df_electron.to_parquet(Path(output_folder) / "cord19_electron_v1.parquet")
    df_microscopy.to_parquet(Path(output_folder) / "cord19_microscopy_v1.parquet")
    df_graphics.to_parquet(Path(output_folder) / "cord19_graphics_2_v1.parquet")
    df_molecular.to_parquet(Path(output_folder) / "cord19_molecular_v1.parquet")
    df_photo.to_parquet(Path(output_folder) / "cord19_photography_v1.parquet")
    df_radiology.to_parquet(Path(output_folder) / "cord19_radiology_v1_2.parquet")
    df_high_modality.to_parquet(
        Path(output_folder) / "cord19_higher-modality_v1.parquet"
    )


if __name__ == "__main__":
    main()
