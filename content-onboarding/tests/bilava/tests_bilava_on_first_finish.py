""" Test cases for the update step in BI-LAVA"""
from datetime import datetime
import pandas as pd

import pytest
from pytest_postgresql import factories
from psycopg.rows import dict_row

import biosearch_core.bilava.offload as bilava
from biosearch_core.data.figure import SubFigureStatus
from biosearch_core.bilava.session import create_session

# path to sql file
# poetry run pytest tests/bilava/tests_bilava_updates.py

postgresql_my_proc = factories.postgresql_proc(host="localhost")
postgresql_my = factories.postgresql("postgresql_my_proc")


@pytest.fixture()
def database(postgresql):
    """Check main postgresql fixture."""
    with open(
        "tests/bilava/create_tables_on_first_finish.sql", "r", encoding="utf-8"
    ) as f_in:
        setup_sql = f_in.read()
    with postgresql.cursor() as cursor:
        cursor.execute(setup_sql)
        postgresql.commit()
    yield postgresql


# pylint: disable=W0621:redefined-outer-name
def test_get_new_session_id(database):
    """Unit test that when processing BI-LAVA on-finish for the first time, the
    session id is 1."""
    schema = "devbilava"
    with database.cursor(row_factory=dict_row) as cursor:
        session_number = bilava.fetch_session_number(cursor, schema)
        assert session_number == 1


def test_create_new_session(database):
    """Unit test for creating a new session object"""
    schema = "devbilava"
    now = datetime.now()

    subfigures = [
        {
            "id": 1,
            "schema": "abc",
            "label": "tomato",
            "upt_label": "orange",
            "upd_date": now,
        },
        {
            "id": 2,
            "schema": "abc",
            "label": "tomato",
            "upt_label": "error.a",
            "upd_date": now,
        },
        {
            "id": 3,
            "schema": "abc",
            "label": "tomato",
            "upt_label": "error.b",
            "upd_date": now,
        },
    ]

    classifiers = ["a", "b", "c"]
    with database.cursor(row_factory=dict_row) as cursor:
        session_number = bilava.fetch_session_number(cursor, schema)
        session = create_session(now, subfigures, classifiers, session_number)
    assert session.number == session_number
    assert session.num_updates == 1
    assert session.num_errors == 2
    assert session.num_classifiers == 3


def test_insert_first_session(database):
    """Unit test for insert a new session object"""
    schema = "devbilava"
    cursor = database.cursor()
    now = datetime.now()

    subfigures = [
        {
            "id": 1,
            "schema": "abc",
            "label": "tomato",
            "upt_label": "orange",
            "upd_date": now,
        }
    ]
    classifiers = ["a"]

    with database.cursor(row_factory=dict_row) as cursor:
        session_id = bilava.record_session(cursor, schema, subfigures, classifiers)
        assert session_id == 1


def test_insert_next_session(database):
    """Unit test that the session ids are correctly gathered after one session exists"""
    schema = "devbilava"
    now = datetime.now()

    subfigures = [
        {
            "id": 1,
            "schema": "abc",
            "label": "tomato",
            "upt_label": "orange",
            "upd_date": now,
        }
    ]
    classifiers = ["a"]

    with database.cursor(row_factory=dict_row) as cursor:
        session_id_1 = bilava.record_session(cursor, schema, subfigures, classifiers)
        assert session_id_1 == 1
        session_number = bilava.fetch_session_number(cursor, schema)
        assert session_number == 2


def test_fetch_affected_figures(database):
    """Unit test for fetching figures from the features table that were updated.
    The list include updates on the labeled and unlabeled values, such as
    mislabels, OoDs, errors, and confirming unlabeled values"""
    schema = "devbilava"
    with database.cursor(row_factory=dict_row) as cursor:
        subfigures = bilava.fetch_affected_subfigures(cursor, schema)
        assert len(subfigures) == 11
        # check the updated labels, by default the 11 checks below validate
        # that there are not other ids in the list that we do not want
        d2subfigs = {(el["id"], el["schema"]): el for el in subfigures}
        assert d2subfigs[(2, "dogs")]["upt_label"] == "bul.1"
        assert d2subfigs[(3, "dogs")]["upt_label"] == "error.cat"
        assert d2subfigs[(4, "dogs")]["upt_label"] == "error.bird"
        assert d2subfigs[(6, "dogs")]["upt_label"] == "bul.2"
        assert d2subfigs[(7, "dogs")]["upt_label"] == "ter.2"
        assert d2subfigs[(9, "dogs")]["upt_label"] == "ter.1"

        assert d2subfigs[(2, "unlabeled")]["upt_label"] == "bul.2"
        assert d2subfigs[(3, "unlabeled")]["upt_label"] == "ter.2"
        assert d2subfigs[(4, "unlabeled")]["upt_label"] == "bul.2"
        assert d2subfigs[(5, "unlabeled")]["upt_label"] == "ter.1"
        assert d2subfigs[(6, "unlabeled")]["upt_label"] == "error.cat"


def test_fetch_affected_classifiers(database):
    """Test fetching affected classifiers in the labeling session"""
    schema = "devbilava"
    with database.cursor(row_factory=dict_row) as cursor:
        classifiers = bilava.fetch_affected_classifiers(cursor, schema)
        assert len(classifiers) == 3
        assert "breeds" in classifiers
        assert "breeds-bulldog" in classifiers
        assert "breeds-terrier" in classifiers


def test_archive_update(database):
    """Test that archiving the updates in the vault store the right values"""
    schema = "devbilava"
    with database.cursor(row_factory=dict_row) as cursor:
        classifiers = bilava.fetch_affected_classifiers(cursor, schema)
        subfigures = bilava.fetch_affected_subfigures(cursor, schema)
        session_id = bilava.record_session(cursor, schema, subfigures, classifiers)

        bilava.archive_updates(cursor, schema, subfigures, session_id)
        results = cursor.execute(f"SELECT * FROM {schema}.archivevault").fetchall()
        assert len(results) == 11
        d2subfigs = {(el["subfig_id"], el["schema"]): el for el in results}
        assert d2subfigs[(2, "dogs")]["label"] == "ter.1"
        assert d2subfigs[(2, "dogs")]["prediction"] == "ter.1"
        assert d2subfigs[(2, "dogs")]["upt_label"] == "bul.1"
        assert d2subfigs[(3, "dogs")]["label"] == "ter.1"
        assert d2subfigs[(3, "dogs")]["prediction"] == "ter.1"
        assert d2subfigs[(3, "dogs")]["upt_label"] == "error.cat"
        assert d2subfigs[(4, "dogs")]["label"] == "ter.1"
        assert d2subfigs[(4, "dogs")]["prediction"] == "ter.2"
        assert d2subfigs[(4, "dogs")]["upt_label"] == "error.bird"
        assert d2subfigs[(6, "dogs")]["label"] == "bul.1"
        assert d2subfigs[(6, "dogs")]["prediction"] == "bul.2"
        assert d2subfigs[(6, "dogs")]["upt_label"] == "bul.2"
        assert d2subfigs[(7, "dogs")]["label"] == "bul.2"
        assert d2subfigs[(7, "dogs")]["prediction"] == "bul.2"
        assert d2subfigs[(7, "dogs")]["upt_label"] == "ter.2"
        assert d2subfigs[(9, "dogs")]["label"] == "ter.2"
        assert d2subfigs[(9, "dogs")]["prediction"] == "ter.2"
        assert d2subfigs[(9, "dogs")]["upt_label"] == "ter.1"
        assert d2subfigs[(2, "unlabeled")]["label"] == "unl"
        assert d2subfigs[(2, "unlabeled")]["prediction"] == "bul.1"
        assert d2subfigs[(2, "unlabeled")]["upt_label"] == "bul.2"
        assert d2subfigs[(3, "unlabeled")]["label"] == "unl"
        assert d2subfigs[(3, "unlabeled")]["prediction"] == "ter.2"
        assert d2subfigs[(3, "unlabeled")]["upt_label"] == "ter.2"
        assert d2subfigs[(4, "unlabeled")]["label"] == "unl"
        assert d2subfigs[(4, "unlabeled")]["prediction"] == "bul.2"
        assert d2subfigs[(4, "unlabeled")]["upt_label"] == "bul.2"
        assert d2subfigs[(5, "unlabeled")]["label"] == "unl"
        assert d2subfigs[(5, "unlabeled")]["prediction"] == "ter.1"
        assert d2subfigs[(5, "unlabeled")]["upt_label"] == "ter.1"
        assert d2subfigs[(6, "unlabeled")]["label"] == "unl"
        assert d2subfigs[(6, "unlabeled")]["prediction"] == "bul.1"
        assert d2subfigs[(6, "unlabeled")]["upt_label"] == "error.cat"
        assert d2subfigs[(6, "unlabeled")]["session_number"] == 1


def test_update_original_subfigures(database):
    """Test updating the figures in the source tables by using the
    schema saved in BI-LAVA"""
    schema = "devbilava"
    with database.cursor(row_factory=dict_row) as cursor:
        subfigures = bilava.fetch_affected_subfigures(cursor, schema)
        bilava.update_original_subfigures(cursor, subfigures)

        # figures that should be updated
        for subfig in subfigures:
            q = f"SELECT status, ground_truth as gt FROM {subfig['schema']}.figures WHERE id={subfig['id']}"
            result = cursor.execute(q).fetchone()
            assert result["gt"] == subfig["upt_label"]
            assert result["status"] == SubFigureStatus.GROUND_TRUTH.value

        # figures that should not be updated
        not_modified_images = [
            (1, "dogs", "bul.2", SubFigureStatus.GROUND_TRUTH.value),
            (5, "dogs", "bul.1", SubFigureStatus.GROUND_TRUTH.value),
            (8, "dogs", "bul.2", SubFigureStatus.GROUND_TRUTH.value),
            (1, "unlabeled", None, SubFigureStatus.PREDICTED.value),
        ]
        for not_modified in not_modified_images:
            q = f"SELECT status, ground_truth as gt FROM {not_modified[1]}.figures WHERE id={not_modified[0]}"
            result = cursor.execute(q).fetchone()
            assert result["gt"] == not_modified[2]
            assert result["status"] == not_modified[3]


def test_parquet_filenames():
    """Test that the new parquet files get correct names"""
    data_folder = "tests/bilava/fake_project/parquets"

    filename = bilava.get_parquet_filename("microscopy", data_folder)
    assert filename == "cord19_microscopy_v2.parquet"
    filename = bilava.get_parquet_filename("higher-modality", data_folder)
    assert filename == "cord19_higher-modality_v11.parquet"


def test_split_dataframes_and_filling_split_set():
    "Test we can split a dataframe into non error and error data"
    # fmt: off
    names = ["i1", "i2", "i3", "i4", "i5", "i6", "i7", "i8", "i9", "i10"]
    labels = ["c1","c2","c3","error.1","error.1","error.2","error.2","error.1","error.1","error.2"]
    split_set = ["TRAIN","TRAIN","VAL","UNL","UNL","UNL","TRAIN","UNL","UNL","UNL"]
    # fmt: on

    columns = ["name", "label", "split_set"]
    input_df = pd.DataFrame(zip(names, labels, split_set), columns=columns)
    df_no_errors, df_err_w_gt, df_err_wo_gt = bilava.split_dataframe_errors(input_df)
    assert len(df_no_errors) == 3
    assert len(df_err_w_gt) == 1
    assert len(df_err_wo_gt) == 6

    df_err_updated = bilava.split_sets(df_err_wo_gt)
    unique_split = df_err_updated.split_set.unique()
    assert "UNL" not in unique_split
    assert "TRAIN" in unique_split
    assert "VAL" in unique_split
    assert "TEST" in unique_split


def test_split_dataframes_and_filling_split_set_with_small_set():
    "Test we can split a dataframe into non error and error data"
    # fmt: off
    names = ["i1", "i2", "i3", "i4", "i5", "i6", "i7", "i8", "i9", "i10"]
    labels = ["c1","c2","c3","c3","c2","c1","c1","error.1","error.1","error.2"]
    split_set = ["TRAIN","TRAIN","VAL","VAL","TRAIN","VAL","TRAIN","UNL","UNL","UNL"]
    # fmt: on

    columns = ["name", "label", "split_set"]
    input_df = pd.DataFrame(zip(names, labels, split_set), columns=columns)
    df_no_errors, df_err_w_gt, df_err_wo_gt = bilava.split_dataframe_errors(input_df)
    assert len(df_no_errors) == 7
    assert len(df_err_w_gt) == 0
    assert len(df_err_wo_gt) == 3

    with pytest.raises(ValueError):
        bilava.split_sets(df_err_wo_gt)


def test_fetch_dataframe_from_labeled_sources_with_higher_classifier(database):
    """Test fetching the dataframe for a higher-modality classifier in the
    situation when we are querying the figures table without any update. This
    scenario is constrained to only check whether we are able to query the table
    correctly, a more complex scenario is described in the following tests."""
    bilava_schema = "devbilava"
    training_schema = "dogs"
    classifier = "breeds"
    mapper = {"breeds": None, "breeds-terrier": "ter.", "breeds-bulldog": "bul."}

    with database.cursor(row_factory=dict_row) as cursor:
        df_images = bilava.create_df_from_labeled_sources(
            cursor, classifier, training_schema, bilava_schema, mapper
        )
        assert df_images is not None
        assert df_images.shape[0] == 10  # only ten in dogs before updates
        assert "error" not in df_images.label.unique()
        # We don't validate the labels here because that's done in the last step


def test_create_training_file_after_updates_for_classifier(database):
    """Test that the parquet file contains the updated data from different
    schemas"""

    bilava_schema = "devbilava"
    data_schemas = ["dogs", "unlabeled"]
    labeled_schema = "dogs"

    mapper = {"breeds": None, "breeds-terrier": "ter.", "breeds-bulldog": "bul."}

    with database.cursor(row_factory=dict_row) as cursor:
        classifiers = bilava.fetch_affected_classifiers(cursor, bilava_schema)
        subfigures = bilava.fetch_affected_subfigures(cursor, bilava_schema)
        session_id = bilava.record_session(
            cursor, bilava_schema, subfigures, classifiers
        )
        bilava.archive_updates(cursor, bilava_schema, subfigures, session_id)
        bilava.update_original_subfigures(cursor, subfigures)

        # test the higher classifier in fake data
        classifier = "breeds"
        assert classifier in classifiers
        df_images = bilava.create_training_file(
            cursor, classifier, data_schemas, bilava_schema, labeled_schema, mapper
        )
        names = df_images.img.values.tolist()
        names.sort()
        assert df_images is not None
        assert df_images.shape[0] == 15
        # fmt: off
        assert names == ["img-1", "img-10", "img-2", "img-3", "img-4", "img-5",  
                        "img-6", "img-7", "img-8", "img-9", "unl-2", "unl-3",
                        "unl-4", "unl-5", "unl-6"]
        # fmt: on
        assert not df_images.split_set.isnull().values.any()
        # check that there are no dots in the labels for higher-modality
        label_levels = df_images.label.values
        label_levels = [len(el.split(".")) for el in label_levels]
        for level in label_levels:
            assert level == 1
        assert "UNL" not in df_images.split_set.unique()
        assert "TRAIN" in df_images.loc[df_images.label == "error"].split_set.unique()

        # Check child classifier bulldogs
        classifier = "breeds-bulldog"
        assert classifier in classifiers
        df_images = bilava.create_training_file(
            cursor, classifier, data_schemas, bilava_schema, labeled_schema, mapper
        )
        names = df_images.img.values.tolist()
        names.sort()
        assert names == ["img-1", "img-2", "img-5", "img-6", "img-8", "unl-2", "unl-4"]
        assert df_images is not None
        assert df_images.shape[0] == 7
        label_levels = df_images.label.values
        label_levels = [len(el.split(".")) for el in label_levels]
        for level in label_levels:
            assert level == 2
        assert "UNL" not in df_images.split_set.unique()

        # Check child classifier terriers
        classifier = "breeds-terrier"
        assert classifier in classifiers
        df_images = bilava.create_training_file(
            cursor, classifier, data_schemas, bilava_schema, labeled_schema, mapper
        )
        names = df_images.img.values.tolist()
        names.sort()
        assert names == ["img-10", "img-7", "img-9", "unl-3", "unl-5"]
        assert df_images is not None
        assert df_images.shape[0] == 5
        label_levels = df_images.label.values
        label_levels = [len(el.split(".")) for el in label_levels]
        for level in label_levels:
            assert level == 2
        assert "UNL" not in df_images.split_set.unique()


def test_save_parquets_on_finish(database):
    """Test that the whole on finish procedure generates three files"""
    bilava_schema = "devbilava"
    output_folder = "tests/bilava/fake_project/parquets"
    data_schemas = ["dogs", "unlabeled"]
    labeled_schema = "dogs"

    mapper = {"breeds": None, "breeds-terrier": "ter", "breeds-bulldog": "bul"}
    with database.cursor(row_factory=dict_row) as cursor:
        filenames = bilava.end_labeling_session(
            cursor=cursor,
            bilava_schema=bilava_schema,
            labeled_schema=labeled_schema,
            output_folder=output_folder,
            schemas=data_schemas,
            mapper=mapper,
        )
        assert len(filenames) == 3
