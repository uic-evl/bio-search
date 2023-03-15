""" Module to process the features, prediction probabilities, and active learning
metrics for bilava's strategy"""

from os import cpu_count, remove
from typing import List, Dict
import logging
from pathlib import Path
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np
from tqdm import tqdm
from psycopg import Connection, connect, Cursor
from rich.console import Console
from rich.progress import track
from image_modalities_classifier.models.predict import (
    RunConfig,
    SingleModalityPredictor,
)
from biosearch_core.db.model import ConnectionParams
from biosearch_core.data.figure import FigureType
from biosearch_core.bilava.bilava_figure import BilavaFigure
from biosearch_core.bilava.classifier import Classifier
from biosearch_core.bilava.neighborhood import calc_hits
from biosearch_core.bilava.reduction import reduce_embeddings
from biosearch_core.bilava.metrics import calc_entropy, calc_margin_sampling


# select training data should also read the parquet files for the split_set
console = Console()


def _merge_values(data: pd.DataFrame, updated_subset: pd.DataFrame) -> pd.DataFrame:
    """merge update dataframes with latest predicted values"""
    data.set_index("uri", inplace=True)
    data.update(updated_subset.set_index("uri"))
    data.reset_index(inplace=True)
    return data


def calc_embeddings_per_schema(
    input_df: pd.DataFrame,
    classifier_path: str,
    schema_2_img_dir: Dict[str, str],
    run_config: RunConfig,
) -> pd.DataFrame:
    """Calculate the embeddings for every image in the dataset. Process goes
    in blocks based on the database schema where the image was retrieved"""
    print("extracting features")
    tmp_df = input_df.copy()
    tmp_df["features"] = None
    features_model = SingleModalityPredictor(classifier_path, run_config)
    for schema in schema_2_img_dir.keys():
        df_schema = tmp_df.loc[tmp_df.schema == schema]
        df_schema = df_schema.drop("features", axis=1)
        if len(df_schema) == 0:
            continue
        embeddings = features_model.features(
            df_schema, schema_2_img_dir[schema], path_col="uri"
        )
        # if features exist before, next sentence raises ValueError
        # better delete and let the merge update the values on the parent
        df_schema.loc[:, "features"] = list(embeddings)
        tmp_df = _merge_values(tmp_df, df_schema)
    return tmp_df


def calc_predictions_per_schema(
    input_df: pd.DataFrame,
    classifier_path: str,
    schema_2_img_dir: Dict[str, str],
    run_config: RunConfig,
) -> pd.DataFrame:
    """Populate dataframe with probablities and predictions"""
    print("predicting labels")
    temp_df = input_df.copy()
    temp_df["prediction"] = None
    temp_df["probs"] = None
    predictor = SingleModalityPredictor(classifier_path, run_config)
    for schema in schema_2_img_dir.keys():
        df_schema = temp_df.loc[temp_df.schema == schema]
        df_schema = df_schema.drop(["prediction", "probs"], axis=1)
        if len(df_schema) == 0:
            continue
        predictions, probabilities = predictor.predict_with_probs(
            df_schema, schema_2_img_dir[schema], path_col="uri"
        )
        df_schema.loc[:, "prediction"] = predictions
        df_schema.loc[:, "probs"] = list(probabilities)
        temp_df = _merge_values(temp_df, df_schema)
    return temp_df


def calc_features_and_dim_values(
    classifier_path: str,
    clf_name: str,
    workdir: str,
    dataframe: pd.DataFrame,
    schema_2_img_dir: Dict[str, str],
    random_state: int = 42,
    batch_size: int = 32,
):
    """Calculate embeddings and predictions for every image in the dataframe,
    and get the projections in 2D and neighborhood hits per dimensionality
    reduction method"""
    clf_args = {
        "classifier_path": classifier_path,
        "schema_2_img_dir": schema_2_img_dir,
        "run_config": RunConfig(batch_size, min(cpu_count(), 4), "cuda:0"),
    }

    # use classifiers to get embeddings, predictions, and probabilities
    img_df = calc_embeddings_per_schema(dataframe, **clf_args)
    tmp_with_embeddings = Path(workdir) / f"{clf_name}_emb.parquet"
    img_df.to_parquet(tmp_with_embeddings)

    img_df = calc_predictions_per_schema(img_df, **clf_args)
    tmp_with_predictions = Path(workdir) / f"{clf_name}_pred.parquet"
    img_df.to_parquet(tmp_with_predictions)

    # metrics for active learning
    print("calculating active learning metrics")
    all_probabilities = np.vstack(img_df.probs)
    img_df["margin_sampling"] = calc_margin_sampling(all_probabilities)
    img_df["entropy"] = calc_entropy(all_probabilities)
    tmp_with_metrics = Path(workdir) / f"{clf_name}_metrics.parquet"
    img_df.to_parquet(tmp_with_metrics)

    # dimensionality reduction
    dim_args = {"input_df": img_df, "random_state": random_state}
    neigh_args = {"label_col": "prediction", "n_neighbors": 6}

    print("projecting PCA")
    img_df["x_pca"], img_df["y_pca"] = reduce_embeddings(method="pca", **dim_args)
    img_df["hits_pca"] = calc_hits(img_df, "x_pca", "y_pca", **neigh_args)
    tmp_with_pca = Path(workdir) / f"{clf_name}_pca.parquet"
    img_df.to_parquet(tmp_with_pca)

    print("projecting UMAP")
    img_df["x_umap"], img_df["y_umap"] = reduce_embeddings(method="umap", **dim_args)
    img_df["hits_umap"] = calc_hits(img_df, "x_umap", "y_umap", **neigh_args)
    tmp_with_umap = Path(workdir) / f"{clf_name}_umap.parquet"
    img_df.to_parquet(tmp_with_umap)

    print("projecting TSNE")
    img_df["x_tsne"], img_df["y_tsne"] = reduce_embeddings(method="tsne", **dim_args)
    img_df["hits_tsne"] = calc_hits(img_df, "x_tsne", "y_tsne", **neigh_args)

    tmp_done = Path(workdir) / f"{clf_name}.parquet"
    img_df.to_parquet(tmp_done)

    remove(tmp_with_embeddings)
    remove(tmp_with_predictions)
    remove(tmp_with_metrics)
    remove(tmp_with_pca)
    remove(tmp_with_umap)

    return img_df


def fetch_split_set(classifier_long_name: str, parquets_dir: str) -> Dict:
    """Get a dictionary of img_path to split_set"""
    parquets_dir = Path(parquets_dir)
    parquet_file = f"{parquets_dir.stem}_{classifier_long_name}_v1.parquet"
    df_clf = pd.read_parquet(parquets_dir / parquet_file)
    df_clf = df_clf[["img_path", "split_set"]]
    df_clf = df_clf.set_index("img_path")
    return df_clf.to_dict("index")


def fetch_from_db(
    conn: Connection, classifier_short_name: str, schemas: List[str]
) -> pd.DataFrame:
    """Fetch dataframe the will be updated for classifier
    Args:
    - classifier: str
      Short name for classifier. For instance, exp.gel for experimental gel
    - schemas: List[str]
      All schemas that will provide inputs for training
    """

    df_schemas = []
    for schema in schemas:
        label = "ground_truth" if schema == "training" else "label"
        # pylint: disable=consider-using-f-string
        query = """SELECT id, name, uri, width, height, source, status, {label} as label
                  FROM {schema}.figures WHERE fig_type={fig_type}
                """.format(
            schema=schema, fig_type=FigureType.SUBFIGURE.value, label=label
        )
        if classifier_short_name != "":  # root has no short-name
            query += f" AND {label} like '{classifier_short_name}.%'"
        # there should be a dot after the classifier short name
        df_schema = sqlio.read_sql_query(query, conn)
        df_schema["schema"] = schema

        df_schemas.append(df_schema)
    return pd.concat(df_schemas)


def onboard_to_df(
    conn_params: ConnectionParams,
    workdir: str,
    classifier: Classifier,
    train_parquets_dir: str,
    schemas_2_base_image_dir: Dict[str, str],
    schemas: List[str],
    batch_size=32,
) -> pd.DataFrame:
    """Retrieve the starting data for bi-lava features table. Data comes from initial
    labeled datasets and from unlabeled data processed from pipeline. The processsed
    data is stored in a dataframe so that a following step can read and insert
    the data into the database.

    Args
    ------
    conn_params: ConnectionParams
      Database params
    classifier: Classifier
      Classifier metadata
    train_parquets_dir: path
      Folder location for the starting labeled training data stored in parquet files.
    schemas_2_base_image_dir: Dict[str, str]
      As different schemas can have the images in different directory locations,
      this dictionary maps the base_img_dir per schema to allow solving the relative paths
    schemas: List[str]
      Schemas in database that provide figures. Training images come from 'training'.
      e.g. ["training", "cord19"]
    """

    # match the split set for the training images
    print("reading split sets from parquet")
    img_path_2_split_set = fetch_split_set(classifier.long_name, train_parquets_dir)
    # pylint: disable=not-context-manager
    print("reading data from database")
    with connect(conninfo=conn_params.conninfo(), autocommit=False) as conn:
        df_db_figures = fetch_from_db(conn, classifier.short_name, schemas)
    # for the starting condition, the data processed from raw papers have only
    # unlabeled data.
    df_db_figures["split_set"] = df_db_figures.apply(
        lambda x: img_path_2_split_set[x.uri]["split_set"]
        if x.uri in img_path_2_split_set
        else "UNL",
        axis=1,
    )
    print("removing duplicates")
    # remove duplicated uri, most likely from training data
    df_db_figures = df_db_figures.set_index("uri")
    df_db_figures = df_db_figures[~df_db_figures.index.duplicated()]
    df_db_figures = df_db_figures.reset_index()

    print("starting features calculation")
    df_processed = calc_features_and_dim_values(
        classifier.model_path,
        classifier.long_name,
        workdir,
        df_db_figures,
        schemas_2_base_image_dir,
        batch_size=batch_size,
    )

    return df_processed


def dataframe_to_bilava_figures(
    classifier: str, input_df_path: str
) -> List[BilavaFigure]:
    """load dataframe data into bilava figures array"""
    figures = []
    input_df = pd.read_parquet(input_df_path)
    input_df = input_df.astype({"id": int, "width": int, "height": int, "status": int})
    for _, row in track(input_df.iterrows(), description="loading from parquet..."):
        bilava_figure = BilavaFigure(
            id=row["id"],
            schema=row["schema"],
            classifier=classifier,
            label=row["label"],
            prediction=row["prediction"],
            name=row["name"],
            uri=row["uri"],
            width=row["width"],
            height=row["height"],
            source=row["source"],
            status=row["status"],
            split_set=row["split_set"],
            x_pca=row["x_pca"],
            y_pca=row["y_pca"],
            x_tsne=row["x_tsne"],
            y_tsne=row["y_tsne"],
            x_umap=row["x_umap"],
            y_umap=row["y_umap"],
            pred_probs=row["probs"].tolist(),
            margin_sample=row["margin_sampling"],
            entropy=row["entropy"],
            hit_pca=row["hits_pca"],
            hit_umap=row["hits_umap"],
            hit_tsne=row["hits_tsne"],
        )
        figures.append(bilava_figure)
    return figures


def insert_classifier_data_to_db(
    classifier: str, df_path: str, bilava_schema: str, cursor: Cursor
):
    """load images from dataframe and insert them into bilava's features table"""
    with console.status(f"[bold green] processing {classifier} data..."):
        console.log("task 1: fetching objects from dataframe")
        bilava_figures = dataframe_to_bilava_figures(classifier, df_path)
        console.log("task 2: copying to db")
        # pylint: disable=line-too-long
        sql = f"COPY {bilava_schema}.features (id, schema, classifier, label, prediction, name, uri, width, height, source, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, status) FROM STDIN"
        with cursor.copy(sql) as copy:
            for figure in bilava_figures:
                copy.write_row(figure.to_tuple())
        console.log(f"tasks for {classifier} completed")


def onboard_to_db(
    conn_params: ConnectionParams, input_df_paths: List[str], bilava_schema: str
) -> bool:
    """Second step for onboarding training and unlabeled data for the first time.
    Import the data from a dataframe to database."""

    console.log("[bold orange] inserting figures to db")
    # pylint: disable=not-context-manager
    with connect(conninfo=conn_params.conninfo(), autocommit=False) as conn:
        try:
            for input_df_path in input_df_paths:
                classifier = Path(input_df_path).stem

                with conn.cursor() as cursor:
                    insert_classifier_data_to_db(
                        classifier=classifier,
                        df_path=input_df_path,
                        bilava_schema=bilava_schema,
                        cursor=cursor,
                    )
                conn.commit()
        # pylint: disable=broad-except
        except Exception as exc:
            console.log(f"[bold red] exception raised {exc}")
            logging.error("Error inserting content", exc_info=True)
            conn.rollback()
            return False
    return True
