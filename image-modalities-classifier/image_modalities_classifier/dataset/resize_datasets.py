""" Scaling the datasets collected externally because the images are too big
compared to the ones obtained from figures in PDFs. In addition, we hope the
smaller images make the training faster.

To decide what datasets to include, you could check the parquet files from the
original sizes in data/0. Print them by bin using:

df = pd.read_parquet(data_path)
bins = 18
groups = df.groupby(["source", pd.cut(df.width, bins)])
groups.size().unstack()
"""
from image_modalities_classifier.dataset.utils import scale_dataset

MAX_SIZE = 400

# "/home/jtt/Documents/datasets/curation_data/x_rays/kaggle_xrays_covid19_pneumonia",
# "/home/jtt/Documents/datasets/curation_data/ct_scans/COVID-CT",
# "/home/jtt/Documents/datasets/curation_data/ct_scans/kaggle_sars_cov2",
# "/home/jtt/Documents/datasets/curation_data/xrays/images",

input_paths = [
    "/home/jtt/Documents/datasets/curation_data/chart_synthetic_1/train",
]


def main():
    """Scale dataset images"""
    for input_path in input_paths:
        output_path = f"{input_path}_{MAX_SIZE}"
        print(output_path)
        scale_dataset(input_path, output_path, MAX_SIZE)


if __name__ == "__main__":
    main()
