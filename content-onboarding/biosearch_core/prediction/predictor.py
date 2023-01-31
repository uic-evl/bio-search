""" Module responsible for predicting the image modalities for the imported
subfigures"""

from os import cpu_count
from typing import Dict, List, Tuple
from pathlib import Path
import logging
from pandas import DataFrame
from torch import cuda
from psycopg import sql, Cursor, connect  # https://github.com/PyCQA/pylint/issues/5273

from image_modalities_classifier.models.predict import ModalityPredictor, RunConfig
from biosearch_core.data.figure import SubFigureStatus, FigureType
from biosearch_core.managers.base import Structure
from biosearch_core.db.model import ConnectionParams


class PredictManager:
    """Manage the predictions on NOT PREDICTED subfigures"""

    def __init__(
        self, project_dir: str, conn_params: ConnectionParams, classifiers: Dict
    ):
        self.params = conn_params
        self.schema = conn_params.schema

        device = "cuda:0" if cuda.is_available() else "cpu"
        self.run_config = RunConfig(
            batch_size=128, num_workers=cpu_count(), device=device
        )
        self.classifiers = classifiers
        self.base_img_path = Path(project_dir) / Structure.TO_PREDICT.value

    def fetch_subfigures_from_db(self, cursor: Cursor) -> List[Tuple]:
        """Fetch not predicted subfigures from db"""
        # pylint: disable=consider-using-f-string
        query = """
          SELECT id, uri 
          FROM {schema}.figures
          WHERE status={status} AND fig_type={type}
        """.format(
            schema=self.schema,
            status=SubFigureStatus.NOT_PREDICTED.value,
            type=FigureType.SUBFIGURE.value,
        )
        cursor.execute(query)
        return cursor.fetchall()

    def _update_db(self, cursor, data: DataFrame) -> None:
        """Update subfigures during prediction phase
        Send the update queries as repeated statements because psycopg3 does
        not have the extra_values functions available in psycopg2.
        """
        tuples = data[["prediction", "id"]]
        tuples = list(tuples.itertuples(index=False, name=None))
        flattened_values = [item for sublist in tuples for item in sublist]

        single_query = f"UPDATE {self.schema}.figures SET status={SubFigureStatus.PREDICTED.value},"
        single_query += " label=('{}') WHERE id=({}); "

        all_queries = single_query * len(tuples)
        query = sql.SQL(all_queries.format(*flattened_values))
        cursor.execute(query)

    def predict(self):
        """Predict label and set status to predicted"""
        # pylint: disable=not-context-manager
        with connect(conninfo=self.params.conninfo(), autocommit=False) as conn:
            output_df = None
            with conn.cursor() as cursor:
                try:
                    # tuples id, img_path
                    rows = self.fetch_subfigures_from_db(cursor)
                    if len(rows) == 0:
                        return None

                    rel_img_paths = [elem[1] for elem in rows]
                    predictor = ModalityPredictor(self.classifiers, self.run_config)
                    # predict does not shuffle
                    output_df = predictor.predict(rel_img_paths, self.base_img_path)
                    output_df["id"] = [elem[0] for elem in rows]
                    self._update_db(cursor, output_df)
                    conn.commit()
                # pylint: disable=bare-except
                except:
                    logging.error("PREDICTION", exc_info=True)
        return output_df
