""" Script to prepare training data for radiology sources """
from image_modalities_classifier.dataset.utils import df_from_disk_no_captions


def main():
    """Create parquet files from radiology datasets collected online"""
    df_cts_sars_cov2 = df_from_disk_no_captions(
        "/media/cumulus/curation_data",
        "ct_scans/kaggle_sars_cov2",
        "rad.cmp",
        "ct",
        "kaggle-ct",
    )
    df_cts_covid_ct = df_from_disk_no_captions(
        "/media/cumulus/curation_data", "ct_scans/COVID-CT", "rad.cmp", "ct", "covid-ct"
    )
    df_xrays_radiography = df_from_disk_no_captions(
        "/media/cumulus/curation_data",
        "x_rays/kaggle_covid_radiography",
        "rad.xra",
        "xray",
        "kaggle-rad",
    )
    df_xrays_chest = df_from_disk_no_captions(
        "/media/cumulus/curation_data",
        "x_rays/kaggle_xrays_covid19_pneumonia",
        "rad.xra",
        "xray",
        "kaggle-chest",
    )

    df_cts_sars_cov2.to_parquet("./cts_sars_cov2.parquet")
    df_cts_covid_ct.to_parquet("./cts_covid_ct.parquet")
    df_xrays_radiography.to_parquet("./xrays_radiograpy.parquet")
    df_xrays_chest.to_parquet("./xrays_chest.to_parquet")


if __name__ == "__main__":
    main()
