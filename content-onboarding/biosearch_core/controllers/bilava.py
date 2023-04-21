""" Functions to support bilava back-end"""
from math import ceil, floor
from os import listdir, remove
from pathlib import Path
import json
import logging
from typing import List, Literal, Dict, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from psycopg import connect, sql, Cursor
from psycopg.rows import dict_row
from biosearch_core.db.model import ConnectionParams
from biosearch_core.data.figure import SubFigureStatus
from biosearch_core.bilava.session import create_session


def fetch_classifiers(project_dir: str) -> List[str]:
    """Load the taxonomy list from the project definitions"""
    classifiers_path = Path(project_dir) / "definitions" / "classifiers.json"
    try:
        with open(classifiers_path, "r", encoding="utf-8") as f_in:
            classifiers_info = json.load(f_in)
        classifiers = []
        fringe = [classifiers_info]
        while len(fringe) > 0:
            node = fringe.pop(0)
            classifiers.append(node["classifier"])
            for child in node["children"]:
                fringe.append(child)
        return classifiers
    except FileNotFoundError:
        logging.error("File not found %s", classifiers_path, exc_info=True)
        return None


def fetch_labels_list(conn_params: ConnectionParams) -> List[str]:
    """Fetch labels from database to fit the taxonomy tree"""

    labels = None
    # pylint: disable=not-context-manager
    with connect(conninfo=conn_params.conninfo()) as conn:
        with conn.cursor() as cursor:
            try:
                query = f"SELECT label from {conn_params.schema}.figures"
                cursor.execute(query)
                labels = cursor.fetchall()
                labels = [elem[0] for elem in labels]
            # pylint: disable=broad-except
            except Exception as exc:
                print("Erorr fetching labels", exc)
                logging.error("Error fetching labels", exc_info=True)
    return labels


classifiers_mapper = {
    "experimental": "exp",
    "gel": "exp.gel",
    "higher-modality": "",
    "microscopy": "mic",
    "molecular": "mol",
    "graphics": "gra",
    "radiology": "rad",
    "photography": "pho",
    "electron": "mic.ele",
}


def fetch_images(
    conn_params: ConnectionParams,
    classifier: str,
    reduction: Literal["pca", "umap", "tsne"],
    split_set: Literal["TRAIN", "TRAIN+UNL", "VAL", "TEST", "UNL", "ALL"],
    schemas_2_base_img_dir: Dict[str, str],
    image_server: str,
):
    """Fetch images from database for projection view"""

    images = None
    lbl_len = len(classifiers_mapper[classifier]) + 4  # . and next level

    # pylint: disable=not-context-manager
    with connect(conninfo=conn_params.conninfo(), row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            try:
                query = """
                 SELECT id, uri, prediction as prd, 
                        LEFT(label, {lbl_len}) as lbl,
                        ROUND(x_{reduction}, 2)::float as x,
                        ROUND(y_{reduction}, 2)::float as y,
                        ROUND(hit_{reduction}, 2)::float as hit,
                        split_set as ss,
                        schema,
                        width,
                        height,
                        ms,
                        en,
                        source,
                        round((SELECT max(probs) from unnest(pred_probs) as probs),2)::float as max_prob,
                        status::int,
                        upt_label
                 FROM {bilava_schema}.features
                 WHERE classifier = '{classifier}' AND (upt_label IS NULL OR upt_label NOT LIKE 'error%')
                """.format(
                    reduction=reduction,
                    classifier=classifier,
                    bilava_schema=conn_params.schema,
                    lbl_len=lbl_len,
                )
                if split_set != "ALL":
                    if split_set == "TRAIN+UNL":
                        query = f"{query} AND (split_set='TRAIN' OR split_set='UNL')"
                    else:
                        query = f"{query} AND split_set='{split_set}'"

                cursor.execute(query)
                images = cursor.fetchall()

                images = [
                    {
                        "dbId": el["id"],
                        "lbl": el["lbl"]
                        if el["status"] == SubFigureStatus.GROUND_TRUTH.value
                        else "unl",
                        "prd": el["prd"],
                        "uri": f"{image_server}/{schemas_2_base_img_dir[el['schema']]}/{el['uri']}",
                        "x": el["x"],
                        "y": el["y"],
                        "hit": el["hit"],
                        "ss": el["ss"],
                        "w": el["width"],
                        "h": el["height"],
                        "ms": el["ms"],
                        "en": el["en"],
                        "sr": el["source"],
                        "mp": el["max_prob"],
                        "ulbl": el["upt_label"],
                    }
                    for el in images
                ]
                unique_labels = list(set(el["lbl"] for el in images))
                if "unl" in unique_labels:
                    unique_labels.remove("unl")
                sources = list(set(el["sr"] for el in images))
                unique_labels.sort()
                sources.sort()
                min_prediction = min([el["mp"] for el in images])
            # pylint: disable=broad-except
            except Exception as exc:
                print("Error fetching labels", exc)
                logging.error("Error fetching labels", exc_info=True)
    return {
        "data": images,
        "labels": unique_labels,
        "sources": sources,
        "minPrediction": min_prediction,
    }


def fetch_image_extras(conn_params: ConnectionParams, db_id: int, classifier: str):
    """Fetch information for the thumbnail details panel"""
    # pylint: disable=not-context-manager
    with connect(conninfo=conn_params.conninfo(), row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            try:
                # pylint: disable=C0209:consider-using-f-string
                query = """
                    SELECT name, pred_probs, source
                    FROM {bilava_schema}.features 
                    WHERE id={db_id} AND classifier='{classifier}'
                """.format(
                    bilava_schema=conn_params.schema, db_id=db_id, classifier=classifier
                )
                cursor.execute(query)
                image = cursor.fetchall()[0]

                if image["source"] == "gdx" or image["source"] == "cord19":
                    query_caption = """
                        SELECT sf.label as lbl, f.caption 
                        FROM {schema}.figures sf, {schema}.figures f 
                        WHERE sf.id={db_id} AND f.id = sf.parent_id
                    """.format(
                        schema=image["source"], db_id=db_id
                    )
                else:
                    caption_schema = "training"
                    query_caption = f"SELECT ground_truth as lbl, caption FROM {caption_schema}.figures WHERE id={db_id}"

                cursor.execute(query_caption)
                record = cursor.fetchall()[0]

                return {
                    "name": image["name"],
                    "probs": [round(float(el), 3) for el in image["pred_probs"]],
                    "caption": record["caption"],
                    "fullLabel": record["lbl"],
                }
            # pylint: disable=broad-except
            except Exception as exc:
                print("Error fetching image extra", exc)
                logging.error("Error fetching image extra", exc_info=True)


def update_image_labels(
    conn_params: ConnectionParams, ids: List[int], label: str
) -> bool:
    """Update the upt_label column with the user specified value. We do not touch
    the label value yet as this column will be updated during the next iteration
    """
    query_params = [(datetime.now(), dbid) for dbid in ids]
    flattened_values = [item for sublist in query_params for item in sublist]

    single_query = f"UPDATE {conn_params.schema}.features SET upt_label='{label}', "
    single_query += "upt_date=('{}') WHERE id=({}); "  # the placeholder

    # pylint: disable=not-context-manager
    with connect(conninfo=conn_params.conninfo(), autocommit=False) as conn:
        with conn.cursor() as cursor:
            try:
                all_queries = single_query * len(query_params)
                query = sql.SQL(all_queries.format(*flattened_values))
                cursor.execute(query)
                conn.commit()
                return True
            # pylint: disable=broad-except
            except Exception as exc:
                print("Error updating features in database", exc)
                logging.error("Error updating features in database", exc_info=True)
                return False


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


classifier_2_short = {
    "higher-modality": None,
    "microscopy": "mic",
    "electron": "mic.ele",
    "graphics": "gra",
    "experimental": "exp",
    "gel": "exp.gel",
    "molecular": "mol",
    "photography": "pho",
    "radiology": "rad",
    "error": "error",
}


def split_dataframe_errors(
    input_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split the dataframe into dataframes without errors, with errors marked
    as ground truth, and without errors marked as ground truth"""
    # fmt: off
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
    df_train = df_set[df_set.split_set == "TRAIN"].reset_index()
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
    num_train = floor(df_len * n_train)
    num_val = ceil(df_len * n_val)
    input_df = input_df.reset_index()

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
    df_no_errors, df_err_w_gt, df_err_wo_gt = split_dataframe_errors(df_input)
    try:
        # try our best to stratify
        df_err_wo_gt_updated = split_sets(df_err_wo_gt, test_size=0.1, val_size=0.1)
    except ValueError:
        # in case stratification fails, do simple divide
        df_err_wo_gt_updated = fill_split_set_for_errors_without_ground_truth(
            df_err_wo_gt
        )

    # update split_set column in db
    if len(df_err_wo_gt_updated) > 0:
        query_params = [
            (schema, sf["split_set"], sf["id"])
            for sf in df_err_wo_gt_updated.iterrows()
        ]
        flattened_values = [item for sublist in query_params for item in sublist]
        single_query = "UPDATE {}.figures SET split_set='{}' WHERE id={}; "
        all_queries = single_query * len(query_params)
        query = sql.SQL(all_queries.format(*flattened_values))
        cursor.execute(query)

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
) -> pd.DataFrame:
    """Fetch the dataframe from the labeled data from the training schema and
    fetching the split_set from BI-LAVA"""
    gt_like = mapper[classifier]

    query = f"""
        SELECT f.id, f.name as img, f.uri as img_path, f.width, f.height, 
               f.ground_truth as label, f.source, f.caption, f.notes as original
        FROM {labeled_schema}.figures f
        WHERE f.ground_truth IS NOT NULL 
    """
    if gt_like is not None:
        query += f" AND f.ground_truth like '{gt_like}%'"
    cursor.execute(query)
    images_without_split = cursor.fetchall()

    # splits for updated and not updated images
    if gt_like:
        query_splits = f"""
            SELECT DISTINCT(id, split_set) as out 
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
            SELECT DISTINCT(id, split_set) as out 
            FROM {bilava_schema}.features 
            WHERE schema='{labeled_schema}'
        """

    splits = cursor.execute(query_splits).fetchall()
    id_2_split = {int(el["out"][0]): el["out"][1] for el in splits}

    for image in images_without_split:
        image["split_set"] = id_2_split[image["id"]]
    df_images = pd.DataFrame.from_dict(images_without_split).reset_index()

    # handle errors if classifier is higher-modality
    if gt_like is None:
        df_images = assign_splits_to_errors(cursor, df_images, labeled_schema)
    if "id" in df_images.columns:
        df_images = df_images.drop(columns=["id"])

    return df_images


def create_df_from_unlabeled_sources(
    cursor: Cursor,
    classifier: str,
    unlabeled_schema: str,
    mapper: Dict[str, Optional[str]],
) -> pd.DataFrame:
    """Fetch the updated ground_trugth data in the unlabeled schema and assign
    everything as training data"""
    gt_like = mapper[classifier]
    query = f"""
                SELECT f.name as img, f.uri as img_path, f.width, f.height, 
                      f.ground_truth as label, f.source, f.caption, 
                      f.notes as original
                FROM {unlabeled_schema}.figures f
                WHERE f.ground_truth IS NOT NULL 
            """
    if gt_like is not None:
        query += f" AND ground_truth like '{gt_like}%'"
    cursor.execute(query)
    results = cursor.fetchall()
    local_df = pd.DataFrame.from_dict(results)
    # TODO: change later to several splits
    local_df["split_set"] = "TRAIN"

    return local_df


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
        if schema == labeled_schema:
            local_df = create_df_from_labeled_sources(cursor, classifier, schema, bilava_schema, mapper)
        else:
            local_df = create_df_from_unlabeled_sources(cursor, classifier, schema, mapper)
        dfs.append(local_df)

    df_images = pd.concat(dfs).reset_index(drop=True)
    # adapt the label to the depth of the classifier
    clf_short = mapper[classifier]
    depth = 1 if clf_short is None else len(clf_short.split(".")) + 1
    df_images["label"] = df_images.apply(
        lambda x: ".".join(x.label.split(".")[:depth]), axis=1
    )
    columns = ["img", "img_path", "width", "height", "label", "source", "caption", "original", "split_set"]
    df_images = df_images[columns]
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
        try:
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
        # pylint: disable=W0702:bare-except
        except Exception as exc:
            logging.error("error finishing labeling session", exc_info=True)
            cleanup(created_filenames)
            raise exc
