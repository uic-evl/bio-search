"Utilities for the dataset module"

from pandas import DataFrame


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
