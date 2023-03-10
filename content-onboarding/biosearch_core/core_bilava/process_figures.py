""" Module to process the features, prediction probabilities, and active learning
metrics for bilava's strategy"""

from os import cpu_count
from typing import List, Dict
from pathlib import Path
from numpy import vstack, mean as np_mean
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.manifold import TSNE
import umap
from psycopg import Connection
from image_modalities_classifier.models.predict import (
    RunConfig,
    SingleModalityPredictor,
)


# select training data should also read the parquet files for the split_set


def calc_margin_sampling(y_pred_prob):
    """Margin sampling"""
    return np.diff(-np.sort(y_pred_prob)[:, ::-1][:, :2])


def calc_entropy(y_pred_prob):
    """Entropy"""
    return -np.nansum(np.multiply(y_pred_prob, np.log(y_pred_prob)), axis=1)


def calc_neighborhood_hit(df, x_col, y_col, n_neighbors=6, column_label="label"):
    """Neighborhood hit"""
    projections = [[i, j] for (i, j) in zip(df[x_col], df[y_col])]
    neigh = NearestNeighbors(n_neighbors=n_neighbors, algorithm="ball_tree").fit(
        projections
    )
    n_hits = []
    for neighborhood in neigh.kneighbors(
        projections, n_neighbors + 1, return_distance=False
    ):
        labels = df.iloc[neighborhood][column_label].values
        targets = [labels[0]] * (len(labels) - 1)
        n_hit = np_mean(targets == labels[1:])
        n_hits.append(n_hit)
    return n_hits


def update_dataframe(
    classifier_path: str,
    dataframe: pd.DataFrame,
    schema_2_img_dir: Dict[str, str],
    random_state: int = 42,
):
    run_config = RunConfig(32, min(cpu_count(), 4), "cuda:0")
    # get features per schema because they may have different image dirs
    print("extracting features")
    features_model = SingleModalityPredictor(classifier_path, run_config)
    all_embeddings = None
    for schema in schema_2_img_dir.keys():
        df_schema = dataframe.loc[dataframe.schema == schema]
        embeddings = features_model.features(
            df_schema, schema_2_img_dir[schema], path_col="uri"
        )
        if all_embeddings is None:
            all_embeddings = embeddings
        else:
            all_embeddings = np.vstack((all_embeddings, embeddings))
    dataframe["features"] = list(all_embeddings)

    # reinstantiate model for predictions
    print("predicting labels")
    predictor = SingleModalityPredictor(classifier_path, run_config)
    all_predictions = None
    all_probabilities = None
    for schema in schema_2_img_dir.keys():
        df_schema = dataframe.loc[dataframe.schema == schema]
        predictions, probabilities = predictor.predict_with_probs(
            df_schema, schema_2_img_dir[schema], path_col="uri"
        )
        if all_predictions is None:
            all_predictions = np.hstack(predictions)
        else:
            all_predictions = np.hstack((all_predictions, predictions))
        if all_probabilities is None:
            all_probabilities = np.vstack(probabilities)
        else:
            all_probabilities = np.vstack((all_probabilities, probabilities))
    dataframe["prediction"] = all_predictions
    dataframe["probs"] = list(all_probabilities)

    # metrics for active learning
    print("calculating active learning metrics")
    all_probabilities = vstack(all_probabilities)
    dataframe["margin_sampling"] = calc_margin_sampling(all_probabilities)
    dataframe["entropy"] = calc_entropy(all_probabilities)

    # pca to 2D
    print("projecting PCA")
    pca = PCA(n_components=2, random_state=random_state)
    embeddings_pca = pca.fit_transform(vstack(dataframe.features))
    dataframe["x_pca"], dataframe["y_pca"] = embeddings_pca[:, 0], embeddings_pca[:, 1]
    dataframe["hits_pca"] = calc_neighborhood_hit(
        dataframe, "x_pca", "y_pca", n_neighbors=6, column_label="prediction"
    )

    # umap to 2D
    print("projecting UMAP")
    umap_reducer = umap.UMAP(random_state=random_state)
    embeddings_umap = umap_reducer.fit_transform(vstack(dataframe.features))
    dataframe["x_umap"], dataframe["y_umap"] = (
        embeddings_umap[:, 0],
        embeddings_umap[:, 1],
    )
    dataframe["hits_umap"] = calc_neighborhood_hit(
        dataframe, "x_umap", "y_umap", n_neighbors=6, column_label="prediction"
    )

    # tsne to 2D
    print("projecting TSNE")
    embedding_tsne = TSNE(n_components=2, perplexity=3).fit_transform(
        vstack(dataframe.features)
    )
    dataframe["x_tsne"], dataframe["y_tsne"] = (
        embedding_tsne[:, 0],
        embedding_tsne[:, 1],
    )
    dataframe["hits_tsne"] = calc_neighborhood_hit(
        dataframe, "x_tsne", "y_tsne", n_neighbors=6, column_label="prediction"
    )
    return dataframe


def fetch_from_db(
    conn: Connection, classifier: str, schemas: List[str]
) -> pd.DataFrame:
    """Fetch dataframe the will be updated for classifier
    Args:
    - classifier: str
      Short name for classifier. For instance, exp.gel for experimental gel
    - schemas: List[str]
      All schemas that will provide inputs for training
    """

    # Fetch from tables to get train, val, test
    # bilava should have a table that matches the split set per classifier
    # the training data should be treated differently... because the split_set
    # does not exist yet? or i should keep a separate insert for the first time.

    df_schemas = []
    for schema in schemas:
        label = "ground_truth" if schema == "training" else "label"
        # pylint: disable=consider-using-f-string
        query = """
                SELECT id, name, uri, width, height, source, status FROM {schema}.figures 
                WHERE {label} like '{classifier}%'
                """.format(
            schema=schema, classifier=classifier, label=label
        )
        df_schema = sqlio.read_sql_query(query, conn)
        df_schema["schema"] = schema

        df_schemas.append(df_schema)
    return pd.concat(df_schemas)
