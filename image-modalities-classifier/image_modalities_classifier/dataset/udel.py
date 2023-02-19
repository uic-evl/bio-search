""" Script for creating the training data from gels/plates shared by udel
"""
from pathlib import Path
import pandas as pd
from image_modalities_classifier.dataset.utils import df_from_disk_no_captions


def main():
    """Load gels and plates from disk"""
    base_dir = "/media/cumulus/curation_data"
    output_path = Path("./data/udel.parquet").resolve()
    print(output_path)

    # Load gels
    dataset_dir = "gels/udel_gel_batch_1/raw"
    df_gels = df_from_disk_no_captions(base_dir, dataset_dir, "exp.gel", "gel", "udel")
    print(df_gels.shape)

    # Load plates
    dataset_dir = "plates/udel_plates_batch_1/raw"
    df_plates = df_from_disk_no_captions(
        base_dir, dataset_dir, "exp.pla", "plate", "udel"
    )
    print(df_plates.shape)

    df_concat = pd.concat([df_gels, df_plates])
    df_concat.to_parquet(output_path)


if __name__ == "__main__":
    main()
