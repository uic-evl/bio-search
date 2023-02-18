""" Script for creating the training data from the clef dataset
Modify the parameters below
"""
import pandas as pd
from pathlib import Path
from image_modalities_classifier.dataset.utils import df_from_disk_with_mapper

mapper = {
    # graphics
    "GFIG": "gra",
    "GFLO": "gra.flow",
    "D3DR": "gra.3dr",
    "DSEC": "gra.sig",
    "DSEE": "gra.sig",
    "DSEM": "gra.sig",
    "GSYS": "gra.oth",
    # molecular
    "GCHE": "mol.che",
    "GGEN": "mol.pro",
    # microscopy
    "DMEL": "mic.elec",
    "DMFL": "mic.flu",
    "DMLI": "mic.lig",
    "DMTR": "mic.elec.tra",
    # radiology
    "DMRAN": "rad.ang",
    "DRCT": "rad.cmp",
    "DRMR": "rad.cmp",
    "DRPE": "rad.cmp",
    "DRUS": "rad.uls",
    "DRXR": "rad.xra",
    # photography
    "DVDM": "pho.der",
    "DVEN": "pho.org",
    "DVOR": "pho.org",
    # experimental
    "GGEL": "exp.gel",
    # other
    "DRCO": "oth",
    "GHDR": "oth",
    "GMAT": "oth",
    "GNCP": "oth",
    "GPLI": "oth",
    "GSCR": "oth",
    "GTAB": "oth",
}


def main():
    """Create parquet files mapping CLEF taxonomy to ours"""
    base_dir = "/media/cumulus/curation_data"
    output_path = Path("./data/clef.parquet").resolve()
    print(output_path)

    # Load clef13
    captions_df = pd.read_parquet("./data/captions_clef13.parquet")
    captions_df = captions_df.set_index("img")

    dataset_dir = "subfigure-classification/2013/train"
    df_clef13_train = df_from_disk_with_mapper(
        base_dir, dataset_dir, mapper, "clef13", captions_df
    )
    dataset_dir = "subfigure-classification/2013/test"
    df_clef13_test = df_from_disk_with_mapper(
        base_dir, dataset_dir, mapper, "clef13", captions_df
    )

    # Load clef 16
    captions_df = pd.read_parquet("./data/captions_clef16.parquet")
    captions_df = captions_df.set_index("img")

    dataset_dir = "subfigure-classification/2016/train"
    df_clef16_train = df_from_disk_with_mapper(
        base_dir, dataset_dir, mapper, "clef16", captions_df
    )
    dataset_dir = "subfigure-classification/2016/test2"
    # use csv to move elements
    df_clef16_test = df_from_disk_with_mapper(
        base_dir, dataset_dir, mapper, "clef16", captions_df
    )

    df_clef = pd.concat(
        [df_clef13_train, df_clef13_test, df_clef16_train, df_clef16_test]
    )
    df_clef.to_parquet(output_path)


if __name__ == "__main__":
    main()
