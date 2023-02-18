""" Script to prepare training data for openi sources """
import pandas as pd
from image_modalities_classifier.dataset.utils import df_from_disk_no_captions


def main():
    """Create parquet files from openi datasets collected online"""
    df_cts = df_from_disk_no_captions(
        "/media/cumulus/curation_data",
        "subfigure-classification/OPENI_CT",
        "rad.cmp",
        "ct",
        "open-i",
    )
    df_microscopy = df_from_disk_no_captions(
        "/media/cumulus/curation_data",
        "subfigure-classification/OPENI_MICROSCOPY",
        "mic",
        "mic",
        "open-i",
    )
    df_mri = df_from_disk_no_captions(
        "/media/cumulus/curation_data",
        "subfigure-classification/OPENI_MRI",
        "rad.cmp",
        "mri",
        "open-i",
    )
    df_ultrasound = df_from_disk_no_captions(
        "/media/cumulus/curation_data",
        "subfigure-classification/OPENI_ULTRASOUND",
        "rad.ult",
        "ultrasound",
        "open-i",
    )
    df_xray = df_from_disk_no_captions(
        "/media/cumulus/curation_data",
        "subfigure-classification/OPENI_XRAY",
        "rad.xra",
        "xray",
        "open-i",
    )

    df_concat = pd.concat([df_cts, df_microscopy, df_mri, df_ultrasound, df_xray])
    df_concat.to_parquet("./openi.parquet")


if __name__ == "__main__":
    main()
