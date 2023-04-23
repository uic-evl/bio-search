""" Test cases for making predictions on the figures table"""
from typing import Dict
import pytest
from pytest_postgresql import factories
from psycopg import Connection
import pandas as pd

from biosearch_core.data.figure import SubFigureStatus
from biosearch_core.db.model import ConnectionParams
from biosearch_core.prediction.predictor import PredictManager

# path to sql file
# poetry run pytest tests/bilava/tests_bilava_updates.py

postgresql_my_proc = factories.postgresql_proc(host="localhost")
postgresql_my = factories.postgresql("postgresql_my_proc")


@pytest.fixture()
def database(postgresql) -> Connection:
    """Check main postgresql fixture."""
    with open(
        "tests/predictions/create_prediction_scenario.sql", "r", encoding="utf-8"
    ) as f_in:
        setup_sql = f_in.read()
    with postgresql.cursor() as cursor:
        cursor.execute(setup_sql)
        postgresql.commit()
    yield postgresql


@pytest.fixture()
def fake_conn_params() -> Dict:
    """Pytest-postgres provides the conn so we can pass some fake params to
    instantiate the PredictManager"""
    return {"host": "a", "port": 1, "user": "a", "password": "a", "dbname": "a"}


# pylint: disable=W0621:redefined-outer-name
def test_fetch_predictions_by_status_ground_truth(database, fake_conn_params):
    """Tests we are able to retrieve all figures with ground truth"""
    fake_conn_params["schema"] = "dogs"
    c_params = ConnectionParams(**fake_conn_params)
    clfs = {}
    ground_truth = SubFigureStatus.GROUND_TRUTH.value

    # query the table with labeled data
    mgt = PredictManager(project_dir="dogs", conn_params=c_params, classifiers=clfs)
    with database.cursor() as cursor:
        results = mgt.fetch_subfigures_from_db(cursor, status=ground_truth)
        assert len(results) == 10

    # query the table with unlabeled data
    fake_conn_params["schema"] = "unlabeled"
    c_params = ConnectionParams(**fake_conn_params)
    mgt = PredictManager(
        project_dir="unlabeled", conn_params=c_params, classifiers=clfs
    )
    with database.cursor() as cursor:
        results = mgt.fetch_subfigures_from_db(cursor, status=ground_truth)
        assert len(results) == 1


def test_fetch_all_figures(database, fake_conn_params):
    """Tests we are able to retrieve all elements from figures table"""

    # query the table with labeled data
    fake_conn_params["schema"] = "dogs"
    c_params = ConnectionParams(**fake_conn_params)
    mgt = PredictManager(project_dir="dogs", conn_params=c_params, classifiers={})
    with database.cursor() as cursor:
        results = mgt.fetch_subfigures_from_db(cursor, status=None)
        assert len(results) == 10

    # query the table with unlabeled data
    fake_conn_params["schema"] = "unlabeled"
    c_params = ConnectionParams(**fake_conn_params)
    mgt = PredictManager(project_dir="unlabeled", conn_params=c_params, classifiers={})
    with database.cursor() as cursor:
        results = mgt.fetch_subfigures_from_db(cursor, status=None)
        assert len(results) == 6


def test_fetch_figures_to_predict(database, fake_conn_params):
    """Tests we are able to figures that need prediction"""
    to_predict = SubFigureStatus.NOT_PREDICTED.value

    # query the table with labeled data
    fake_conn_params["schema"] = "dogs"
    c_params = ConnectionParams(**fake_conn_params)
    mgt = PredictManager(project_dir="dogs", conn_params=c_params, classifiers={})
    with database.cursor() as cursor:
        results = mgt.fetch_subfigures_from_db(cursor, status=to_predict)
        assert len(results) == 0

    # query the table with unlabeled data
    fake_conn_params["schema"] = "unlabeled"
    c_params = ConnectionParams(**fake_conn_params)
    mgt = PredictManager(project_dir="unlabeled", conn_params=c_params, classifiers={})
    with database.cursor() as cursor:
        results = mgt.fetch_subfigures_from_db(cursor, status=to_predict)
        assert len(results) == 2


def test_invalid_status(database, fake_conn_params):
    """Test we only get figures with valid status"""
    fake_conn_params["schema"] = "unlabeled"
    c_params = ConnectionParams(**fake_conn_params)
    error_status = 50

    mgt = PredictManager(project_dir="dogs", conn_params=c_params, classifiers={})
    with database.cursor() as cursor:
        with pytest.raises(ValueError):
            mgt.fetch_subfigures_from_db(cursor, status=error_status)


def test_fetch_gt_figures_from_dataframe(database, fake_conn_params):
    """Test that we are parsing correctly the values from the dataframe"""
    to_update = [{"id": 1, "prediction": "bul.2"}, {"id": 2, "prediction": "ter.2"}]
    df_update = pd.DataFrame.from_dict(to_update)

    fake_conn_params["schema"] = "dogs"
    c_params = ConnectionParams(**fake_conn_params)
    mgt = PredictManager(project_dir="dogs", conn_params=c_params, classifiers={})
    with database.cursor() as cursor:
        # pylint: disable=W0212:protected-access
        results = mgt._fetch_ids_with_ground_truth(cursor, df_update)
        assert len(results) == 2
        assert 1 in results
        assert 2 in results


def test_update_schema_unlabeled_samples(database: Connection, fake_conn_params):
    """Test that we update a table with unlabeled samples and we do not alter
    any status for images already with ground truth labels"""

    to_update = [
        {"id": 1, "prediction": "ter.2"},
        {"id": 2, "prediction": "bul.1"},
        {"id": 3, "prediction": "bul.1"},
    ]
    df_update = pd.DataFrame.from_dict(to_update)

    schema = "unlabeled"
    fake_conn_params["schema"] = schema
    c_params = ConnectionParams(**fake_conn_params)
    mgt = PredictManager(project_dir="unlabeled", conn_params=c_params, classifiers={})

    with database.cursor() as cursor:
        # pylint: disable=W0212:protected-access
        mgt._update_db(cursor, df_update)
        query = f"SELECT id, label, status FROM {schema}.figures"
        d_results = {el[0]: el for el in cursor.execute(query).fetchall()}

        # check ground truth
        assert d_results[1][1] == "ter.2"
        assert d_results[2][1] == "bul.1"
        assert d_results[3][1] == "bul.1"
        # check status
        assert d_results[1][2] == SubFigureStatus.GROUND_TRUTH.value
        assert d_results[2][2] == SubFigureStatus.PREDICTED.value
        assert d_results[3][2] == SubFigureStatus.PREDICTED.value
