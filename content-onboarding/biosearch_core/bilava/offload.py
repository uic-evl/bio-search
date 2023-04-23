""" Module that supports the offloading operations from BI-LAVA after labeling.
The offloading workflow contemplates taking the updates from the features table,
archiving updates in the database for comparisons across time, and updating 
any table that provided figures to the labeling session.

Database operations:
The operations in this module leverage psycopg cursors using dict_row. This 
parameter ensures that the rows specified by the queries are returned as
List[Dict] instead of List[Tuple].

Test cases:
tests/bilava/tests_bilava_on_first_finish.py
run: poetry run pytest -s tests/bilava/tests_bilava_on_first_finish.py 
"""
from sys import argv
from math import ceil, floor
from os import listdir, remove
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging
from argparse import ArgumentParser, Namespace
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit
from psycopg import sql, Cursor, connect
from psycopg.rows import dict_row
from biosearch_core.data.figure import SubFigureStatus
from biosearch_core.bilava.session import create_session
from biosearch_core.db.model import ConnectionParams, params_from_env


def fetch_affected_classifiers(cursor: Cursor, schema: str) -> List[str]:
    """Grab from the bilava work table every classifier where the images were updated"""
    query = f"""SELECT classifier, COUNT(classifier)
                FROM {schema}.features 
                WHERE upt_label IS NOT NULL GROUP BY classifier"""
    cursor.execute(query)
    records = cursor.fetchall()
    return [el["classifier"] for el in records]


def fetch_affected_subfigures(cursor: Cursor, schema: str) -> List[Dict]:
    """Fetch the list of figures updated during the labeling session.
    BI-LAVA duplicates each figure row for each classifier where it appears in
    the features table. However, once we update a label, it propagate the update
    for every copy on the table based on the figure id. Therefore, to retrieve
    the unique figures we need to group by the record from the features table.
    The label and upt_label values store the full label so the STRING_AGG will
    return one value despite being concatenated.
    BI-LAVA considers and update to every element that has an up_label value
    on the table. For unlabeled data, having a label == upt_label means that
    we are confirming the predicted label and making it ground truth. For labeled
    data, label == upt_label should not happen because it's redundant and it's
    controlled by the application during the interactions.

    Args:
        - cursor: Database cursor
        - schema: BI-LAVA schema

    Returns:
        List of dictionary entries where each dictionary has the keys
        'id', 'schema', 'label', 'upt_label', 'upt_date'.
        The schema value indicates what schema in the database stores the original
        row for the subfigure
    """
    # pylint: disable=C0209:consider-using-f-string
    query = """
        SELECT id, schema, 
               STRING_AGG(DISTINCT label, ',') as label,
               STRING_AGG(DISTINCT prediction, ',') as prediction,
               STRING_AGG(DISTINCT upt_label, ',') as upt_label,
               STRING_AGG(DISTINCT CAST(upt_date AS text), ',') as upt_date,
               STRING_AGG(DISTINCT split_set, ',') as split_set
        FROM {schema}.features 
        WHERE upt_label IS NOT NULL 
        GROUP BY id, schema
        ORDER BY 1
    """.format(
        schema=schema
    )
    results = cursor.execute(query).fetchall()
    for figure in results:
        if figure["split_set"] == "UNL":
            figure["label"] = "unl"
        # because the prediction can be concatenated, grab the longest prediction
        predictions = figure["prediction"].split(",")
        lengths = [len(el) for el in predictions]
        figure["prediction"] = predictions[np.argmax(lengths)]
    return results


def fetch_session_number(cursor: Cursor, schema: str) -> int:
    """Fetch consecutive session number"""
    query_session_id = f"SELECT MAX(number) as num FROM {schema}.session"
    cursor.execute(query_session_id)
    record = cursor.fetchone()["num"]

    session_number = 1
    if record is not None:
        session_number = record + 1
    return session_number


def record_session(
    cursor: Cursor, schema: str, subfigures: List[Dict], classifiers: List[str]
):
    """Record a summary of the changes in the database"""
    end_date = datetime.now()
    session_number = fetch_session_number(cursor, schema)
    session = create_session(end_date, subfigures, classifiers, session_number)

    # pylint: disable=C0209:consider-using-f-string
    insert_query = """
        INSERT INTO {schema}.session(end_date, "number", num_updates, num_errors, num_classifiers)
	    VALUES ('{end_date}', {number}, {num_updates}, {num_errors}, {num_classifiers})
        RETURNING id;
    """.format(
        schema=schema,
        number=session_number,
        end_date=session.end_date,
        num_updates=session.num_updates,
        num_errors=session.num_errors,
        num_classifiers=session.num_classifiers,
    )
    results = cursor.execute(insert_query).fetchone()
    session_id = results["id"]

    return session_id


def archive_updates(
    cursor: Cursor, schema: str, subfigures: List[Dict], session_id: int
):
    """Archive the session updates in the database"""
    insert_sql = f"COPY {schema}.archivevault (subfig_id,schema,label,upt_label,upt_date,session_number,prediction) FROM STDIN"
    with cursor.copy(insert_sql) as copy:
        for subfig in subfigures:
            copy.write_row(
                (
                    subfig["id"],
                    subfig["schema"],
                    subfig["label"],
                    subfig["upt_label"],
                    subfig["upt_date"],
                    session_id,
                    subfig["prediction"],
                )
            )


def update_original_subfigures(cursor: Cursor, subfigures: List[Dict]):
    """Update the ground truth value on the figure data sources.
    Use the schema to point to the right tables. For instance, the cord19 unlabeled
    data is in one schema while the training data is in another schema.
    """
    query_params = [
        (
            sf["schema"],
            sf["upt_label"],
            datetime.now(),
            SubFigureStatus.GROUND_TRUTH.value,
            sf["id"],
        )
        for sf in subfigures
    ]
    flattened_values = [item for sublist in query_params for item in sublist]
    single_query = "UPDATE {}.figures SET ground_truth='{}', last_update_by='{}', status={} WHERE id={}; "
    all_queries = single_query * len(query_params)
    query = sql.SQL(all_queries.format(*flattened_values))
    cursor.execute(query)


def get_parquet_filename(classifier: str, output_folder: str) -> str:
    """Get filename with new version for training file"""
    base_name = f"cord19_{classifier}_v"
    candidates = [
        el[:-8]
        for el in listdir(output_folder)
        if base_name in el and el.endswith(".parquet")
    ]
    # get the v{number} and get rid of the v
    versions = [int(el.split("_")[-1][1:]) for el in candidates]
    new_version = max(versions) + 1
    return f"{base_name}{new_version}.parquet"


def split_dataframe_errors(
    input_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split the dataframe into dataframes without errors, with errors marked
    as ground truth, and without errors marked as ground truth"""
    # fmt: off
    print(input_df.shape)
    df_errors_wo_gt = input_df.loc[(input_df.label.str.contains("error") & (input_df.split_set == "UNL"))].reset_index(drop=True)
    df_errors_w_gt = input_df.loc[(input_df.label.str.contains("error") & (input_df.split_set != "UNL"))].reset_index(drop=True)
    df_no_errors = input_df.loc[~input_df.label.str.contains("error")].reset_index(drop=True)
    # fmt: on
    return df_no_errors, df_errors_w_gt, df_errors_wo_gt


def split_sets(
    data: pd.DataFrame,
    test_size: float = 0.2,
    val_size: float = 0.1,
    random_state: int = 42,
):
    """Split by label"""
    df_set = data.copy().reset_index(drop=True)
    y = df_set.label
    sss = StratifiedShuffleSplit(
        n_splits=5, test_size=test_size, random_state=random_state
    )
    for _, (train_index, test_index) in enumerate(sss.split(df_set, y)):
        df_set.loc[test_index, "split_set"] = "TEST"
        df_set.loc[train_index, "split_set"] = "TRAIN"

    df_test = df_set[df_set.split_set == "TEST"].reset_index()
    df_train = df_set[df_set.split_set == "TRAIN"].reset_index(drop=True)
    y_train = df_train.label

    # split for validation
    num_val = ceil(df_set.shape[0] * val_size)
    val_test_size = num_val / df_train.shape[0]

    try:
        sss = StratifiedShuffleSplit(
            n_splits=5, test_size=val_test_size, random_state=random_state
        )
        for _, (train_index, test_index) in enumerate(sss.split(df_train, y_train)):
            df_train.loc[test_index, "split_set"] = "VAL"
            df_train.loc[train_index, "split_set"] = "TRAIN"
    except ValueError:
        # when the least populated class in y has only 1 member, needs > 2
        # then do a simple assignment
        df_train.loc[df_train.index < num_val, "split_set"] = "VAL"

    if "index" in df_train.columns:
        df_train = df_train.drop(columns=["index"])
    return pd.concat([df_train, df_test]).reset_index(drop=True)


def fill_split_set_for_errors_without_ground_truth(
    input_df: pd.DataFrame, n_train=0.8, n_val=0.1
) -> pd.DataFrame:
    """Fill the split_set based on a partition n_train/n_val/1-n_train+n_val"""
    df_len = len(input_df)
    num_train = ceil(df_len * n_train)
    num_val = ceil(df_len * n_val)
    input_df = input_df.reset_index(drop=True)

    # fmt: off
    input_df.loc[input_df.index < num_train, 'split_set'] = 'TRAIN'
    input_df.loc[(input_df.index >= num_train) & (input_df.index < num_train+num_val), 'split_set'] = 'VAL'
    input_df.loc[input_df.index >= num_train + num_val, 'split_set'] = 'TEST'
    # fmt: on
    return input_df.drop(columns=["index"])


def assign_splits_to_errors(
    cursor: Cursor, df_input: pd.DataFrame, schema: str
) -> pd.DataFrame:
    """Process the images with errors as labels. In case these images do not have
    a split_set for training the classifier, assign one and save it to db"""
    # TODO: This actually assigns all the split sets to every dataframe, not only errors
    df_no_errors, df_err_w_gt, df_err_wo_gt = split_dataframe_errors(df_input)

    if len(df_err_wo_gt) > 0:
        try:
            # try our best to stratify
            df_err_wo_gt_updated = split_sets(df_err_wo_gt, test_size=0.1, val_size=0.1)
        except ValueError:
            logging.info("stratified split failed, trying simple split")
            # in case stratification fails, do simple divide
            df_err_wo_gt_updated = fill_split_set_for_errors_without_ground_truth(
                df_err_wo_gt
            )
    else:
        df_err_wo_gt_updated = df_err_wo_gt

    # for images without errors, set unlabeled data to train
    df_no_errors.loc[df_no_errors.split_set == "UNL", "split_set"] = "TRAIN"

    # update split_set column in db
    # if len(df_err_wo_gt_updated) > 0:
    #     query_params = [
    #         (schema, sf["split_set"], sf["id"])
    #         for _, sf in df_err_wo_gt_updated.iterrows()
    #     ]
    #     flattened_values = [item for sublist in query_params for item in sublist]
    #     single_query = "UPDATE {}.figures SET split_set='{}' WHERE id={}; "
    #     all_queries = single_query * len(query_params)
    #     query = sql.SQL(all_queries.format(*flattened_values))
    #     cursor.execute(query)

    df_out = pd.concat([df_no_errors, df_err_w_gt, df_err_wo_gt_updated])
    if "index" in df_out.columns:
        df_out = df_out.drop(columns=["index"])
    if "level_0" in df_out.columns:
        df_out = df_out.drop(columns=["level_0"])
    return df_out


def create_df_from_labeled_sources(
    cursor: Cursor,
    classifier: str,
    labeled_schema: str,
    bilava_schema: str,
    mapper: Dict[str, Optional[str]],
) -> Optional[pd.DataFrame]:
    """Fetch the dataframe from the labeled data from the training schema and
    fetching the split_set from BI-LAVA"""
    gt_like = mapper[classifier]

    query = f"""
        SELECT f.id, f.name as img, f.uri as img_path, f.width, f.height, 
               f.ground_truth as label, f.source, f.caption, f.notes as original
        FROM {labeled_schema}.figures f
        WHERE f.ground_truth IS NOT NULL and f.fig_type=1 
    """
    if gt_like is not None:
        query += f" AND f.ground_truth like '{gt_like}%'"

    cursor.execute(query)
    images_without_split = cursor.fetchall()

    if len(images_without_split) == 0:
        return None

    # splits for updated and not updated images
    if gt_like:
        query_splits = f"""
            SELECT DISTINCT(uri, split_set) as out 
            FROM {bilava_schema}.features 
            WHERE schema='{labeled_schema}' AND 
                (   
                    (upt_label is NULL AND label like '{gt_like}%') 
                    OR 
                    (upt_label like '{gt_like}%')
                )
        """
    else:
        query_splits = f"""
            SELECT DISTINCT(uri, split_set) as out 
            FROM {bilava_schema}.features 
            WHERE schema='{labeled_schema}'
        """

    splits = cursor.execute(query_splits).fetchall()
    id_2_split = {el["out"][0]: el["out"][1] for el in splits}

    for image in images_without_split:
        image["split_set"] = id_2_split[image["img_path"]]  # id_2_split[image["id"]]
    df_images = pd.DataFrame.from_dict(images_without_split).reset_index()

    # handle errors if classifier is higher-modality, and split sets
    # if gt_like is None:
    df_images = assign_splits_to_errors(cursor, df_images, labeled_schema)
    if "id" in df_images.columns:
        df_images = df_images.drop(columns=["id"])

    return df_images


# def create_df_from_unlabeled_sources(
#     cursor: Cursor,
#     classifier: str,
#     unlabeled_schema: str,
#     bilava_schema: str,
#     mapper: Dict[str, Optional[str]],
# ) -> pd.DataFrame:
#     """Fetch the updated ground_trugth data in the unlabeled schema and assign
#     everything as training data"""
#     gt_like = mapper[classifier]
#     query = f"""
#                 SELECT f.name as img, f.uri as img_path, f.width, f.height,
#                       f.ground_truth as label, f.source, f.caption,
#                       f.notes as original
#                 FROM {unlabeled_schema}.figures f
#                 WHERE f.ground_truth IS NOT NULL and f.fig_type=1
#             """
#     if gt_like is not None:
#         query += f" AND ground_truth like '{gt_like}%'"
#     cursor.execute(query)
#     results = cursor.fetchall()

#     # splits for updated and not updated images
#     if gt_like:
#         query_splits = f"""
#             SELECT DISTINCT(uri, split_set) as out
#             FROM {bilava_schema}.features
#             WHERE schema='{unlabeled_schema}' AND
#                 (
#                     (upt_label is NULL AND label like '{gt_like}%')
#                     OR
#                     (upt_label like '{gt_like}%')
#                 )
#         """
#     else:
#         query_splits = f"""
#             SELECT DISTINCT(uri, split_set) as out
#             FROM {bilava_schema}.features
#             WHERE schema='{unlabeled_schema}'
#         """

#     splits = cursor.execute(query_splits).fetchall()
#     id_2_split = {el["out"][0]: el["out"][1] for el in splits}

#     for image in results:
#         image["split_set"] = id_2_split[image["img_path"]]
#     local_df = pd.DataFrame.from_dict(results).reset_index()

#     # TODO: change later to several splits
#     # handle errors if classifier is higher-modality
#     if gt_like is None:
#         local_df = assign_splits_to_errors(cursor, local_df, unlabeled_schema)
#     else:
#         local_df["split_set"] = "TRAIN"
#     if "id" in local_df.columns:
#         local_df = local_df.drop(columns=["id"])

#     return local_df


def create_training_file(
    cursor: Cursor,
    classifier: str,
    schemas: List[str],
    bilava_schema: str,
    labeled_schema: str,
    mapper: Dict[str, Optional[str]],
) -> pd.DataFrame:
    """Query schemas to get training data for classifier"""
    dfs = []
    # fmt: off
    for schema in schemas:
        # if schema == labeled_schema:
        local_df = create_df_from_labeled_sources(cursor, classifier, schema, bilava_schema, mapper)
        # else:
        #     local_df = create_df_from_unlabeled_sources(cursor, classifier, schema, bilava_schema, mapper)
        if local_df is not None:
            dfs.append(local_df)

    df_images = pd.concat(dfs).reset_index(drop=True)
    # adapt the label to the depth of the classifier
    clf_short = mapper[classifier]
    depth = 1 if clf_short is None else len(clf_short.split("."))
    df_images["label"] = df_images.apply(
        lambda x: ".".join(x.label.split(".")[:depth]), axis=1
    )
    columns = ["img", "img_path", "width", "height", "label", "source", "caption", "original", "split_set"]
    df_images = df_images[columns]

    # TODO: temp fix for paths
    df_images["img_path"] = df_images.apply(lambda x: x.img_path if x.source != "cord19" else "biosearch/cord19/to_predict/" + x.img_path, axis=1)
    df_images["is_gt"] = True
    # fmt: on
    return df_images


def export_parquet(
    cursor: Cursor,
    classifier: str,
    output_folder: str,
    data_schemas: List[str],
    bilava_schema: str,
    labeled_schema: str,
    mapper: Dict[str, Optional[str]],
):
    """Create parquet file and save it to location"""
    parquet_name = get_parquet_filename(classifier, output_folder)
    df_images = create_training_file(
        cursor, classifier, data_schemas, bilava_schema, labeled_schema, mapper
    )
    filename = Path(output_folder) / parquet_name
    df_images.to_parquet(filename)
    del df_images
    return filename


def cleanup(created_files: List[str]):
    """In case of errors, delete the created files"""
    for filepath in created_files:
        f_path = Path(filepath)
        if f_path.exists():
            try:
                remove(f_path)
            except PermissionError:
                logging.error("could not delete file %s", filepath, exc_info=True)


def end_labeling_session(
    cursor: Cursor,
    bilava_schema: str,
    labeled_schema: str,
    output_folder: str,
    schemas: List[str],
    mapper: Dict[str, Optional[str]],
):
    """Collect the updated labels, update the required tables and create the
    training files. The connection needs to return row_factory=dict_row to
    treat returning elements as dictionaries and not tuples.
    """
    created_filenames = []  # parquet file names to create

    with cursor:
        # get the classifier names that will need to be updated
        classifiers = fetch_affected_classifiers(cursor, bilava_schema)
        # get the record of changes per subfigure
        subfigures = fetch_affected_subfigures(cursor, bilava_schema)
        # record the session
        session_id = record_session(cursor, bilava_schema, subfigures, classifiers)
        # record the changes in the session
        archive_updates(cursor, bilava_schema, subfigures, session_id)
        # update the ground truth values in the original subfigures
        update_original_subfigures(cursor, subfigures)
        # create new parquet records
        # need to move the data so its under /curation_data
        for classifier in classifiers:
            f_name = export_parquet(
                cursor,
                classifier,
                output_folder,
                schemas,
                bilava_schema,
                labeled_schema,
                mapper,
            )
            created_filenames.append(f_name)
        return created_filenames


def setup_logger(workspace: str):
    """configure logger"""
    logger_dir = Path(workspace) / "logs"
    if not logger_dir.exists:
        raise FileNotFoundError("workspace does not exist")

    logging.basicConfig(
        filename=str(logger_dir / "offboard.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def parse_args(args) -> Namespace:
    """Parse args from command line"""
    # fmt: off
    parser = ArgumentParser(prog="BI-LAVA offloader")
    parser.add_argument("workspace", type=str, help="artifacts directory")
    parser.add_argument("db", type=str, help="path to .env with db conn")
    parser.add_argument("-ls", "--labeled_schema", type=str, required=True)
    parser.add_argument("-o", "--output_folder", type=str, required=True)
    parser.add_argument('-ds','--data_schemas', nargs='+', help='Schemas for figures', required=True)
    parsed_args = parser.parse_args(args)
    # fmt: on
    return parsed_args


def main(
    args: Namespace,
    db_params: ConnectionParams,
    bilava_schema: str,
    mapper: Dict[str, Optional[str]],
):
    """Main entry point when executing the offboard logic from script"""
    # pylint: disable=E1129:not-context-manager
    with connect(
        conninfo=db_params.conninfo(), row_factory=dict_row, autocommit=False
    ) as conn:
        with conn.cursor() as cursor:
            created_filenames = None
            try:
                created_filenames = end_labeling_session(
                    cursor,
                    bilava_schema,
                    args.labeled_schema,
                    args.output_folder,
                    args.data_schemas,
                    mapper,
                )
                conn.commit()
                logging.info("Offload completed")
            # pylint: disable=W0702:bare-except
            except Exception as exc:
                logging.error("error finishing labeling session", exc_info=True)
                if created_filenames:
                    cleanup(created_filenames)
                raise exc


if __name__ == "__main__":
    script_args = parse_args(argv[1:])
    conn_params = params_from_env(script_args.db)
    setup_logger(script_args.workspace)

    app_schema = conn_params.schema
    classifiers_mapper = {
        "higher-modality": None,
        "microscopy": "mic.",
        "electron": "mic.ele.",
        "graphics": "gra.",
        "experimental": "exp.",
        "gel": "exp.gel.",
        "molecular": "mol.",
        "photography": "pho.",
        "radiology": "rad.",
        "error": "error",
    }

    main(script_args, conn_params, app_schema, classifiers_mapper)
