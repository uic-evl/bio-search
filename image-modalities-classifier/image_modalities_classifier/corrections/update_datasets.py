""" Fix for parquet files processed in BI-LAVA.
Why:
The parquet files contain None values in the label column when the image comes
from the CORD19 collection. This is correct as that data does not have ground
truth, but a prediction. However, it will be easier to add the label value for
every element and differentiate the nature of the annotation in another column.
Consequently, a row can be distinguished as being a pseudo label or not, and
pseudo-label is also in the label column.
Implications:
When sending a parquet file to train, indicate whether the training set should
include pseudo labels or not. This logic should be included as part of the
training module and invoked from the active learning strategy.
 """

from pathlib import Path
from argparse import ArgumentParser, Namespace
import pandas as pd


def update_dataframe(dataframe: pd.DataFrame):
    """Add the is_gt column to identify content from the cord19 collection as
    not having ground truth data, and update the labels columns to not contain None values"""
    output_df = dataframe.copy()
    output_df["is_gt"] = output_df.apply(lambda row: not row.source == "cord19", axis=1)
    output_df["label"] = output_df.apply(
        lambda row: row.prediction if row.label is None else row.label, axis=1
    )
    output_df.head()
    return output_df


def main(df_filepath: str, output_dir: str) -> None:
    """Process script"""
    df_path = Path(df_filepath)
    original_df = pd.read_parquet(df_path)
    updated_df = update_dataframe(original_df)
    output_path = Path(output_dir) / df_path.name
    updated_df.to_parquet(output_path.resolve(), engine="pyarrow", index=False)


def parse_args() -> Namespace:
    """Read arguments from command line"""
    parser = ArgumentParser(prog="correct missing data in parquet files")
    parser.add_argument(
        "input_filepath",
        type=str,
        help="File path to parquet file to process",
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Where to place updated parquet file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.input_filepath, args.output_dir)
