from pandas import DataFrame
from sklearn.neighbors import NearestNeighbors
from numpy import mean as np_mean
from torch.cuda import device_count
from cuml.neighbors import NearestNeighbors as cumlNearestNeighbors


def calc_neighborhood_hit_cpu(input_df, x_col, y_col, n_neighbors=6, label_col="label"):
    """Neighborhood hit"""
    projections = [[i, j] for (i, j) in zip(input_df[x_col], input_df[y_col])]
    neigh = NearestNeighbors(n_neighbors=n_neighbors, algorithm="ball_tree").fit(
        projections
    )
    n_hits = []
    for neighborhood in neigh.kneighbors(
        projections, n_neighbors + 1, return_distance=False
    ):
        labels = input_df.iloc[neighborhood][label_col].values
        targets = [labels[0]] * (len(labels) - 1)
        n_hit = np_mean(targets == labels[1:])
        n_hits.append(n_hit)
    return n_hits


def calc_neighborhood_hit_gpu(input_df, x_col, y_col, n_neighbors=6, label_col="label"):
    """Calculate the neighborhood hit for each data point.
    Data points with low scores have a considerable proportion of neighbors with
    different predicted labels.

    Attributes
    -----------
    df: pandas dataframe
    embeddings: 2D numpy.ndarray
    """
    projections = input_df[[x_col, y_col]].to_numpy()
    neigh = cumlNearestNeighbors(n_neighbors=n_neighbors, algorithm="brute").fit(
        projections
    )

    n_hits = []
    for neighborhood in neigh.kneighbors(
        projections, n_neighbors + 1, return_distance=False
    ):
        labels = input_df.iloc[neighborhood][label_col].values
        # labels = le.transform(input_df.iloc[neighborhood][label_col].values)
        targets = [labels[0]] * (len(labels) - 1)
        n_hit = np_mean(targets == labels[1:])
        n_hits.append(n_hit)
    return n_hits


def calc_hits(
    input_df: DataFrame, x_col: str, y_col: str, label_col: str, n_neighbors=6
):
    """Calculate the neighborhood hit for each data point. Data points with
    low scores have a considerable proportion of neighbors with different predicted
    labels."""
    if device_count() > 0:
        return calc_neighborhood_hit_gpu(
            input_df, x_col, y_col, n_neighbors=n_neighbors, label_col=label_col
        )
    return calc_neighborhood_hit_cpu(
        input_df, x_col, y_col, n_neighbors=n_neighbors, label_col=label_col
    )
