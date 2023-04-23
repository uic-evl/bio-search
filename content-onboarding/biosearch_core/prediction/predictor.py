""" Module responsible for predicting the image modalities for images in db.
The updates can be performed on non-predicted figures (when importing
content from the pipeline), or to all the figures on a schema (when classifiers
are updated).
"""

from os import cpu_count
from typing import Dict, List, Tuple, Literal, Optional
from pathlib import Path
import logging
from pandas import DataFrame
from torch import cuda
from psycopg import sql, Cursor, connect  # https://github.com/PyCQA/pylint/issues/5273

from image_modalities_classifier.models.predict import ModalityPredictor, RunConfig
from biosearch_core.data.figure import SubFigureStatus, FigureType
from biosearch_core.db.model import ConnectionParams


class PredictManager:
    """Manage the predictions on subfigures"""

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
        self.base_img_path = Path(project_dir) / "to_predict"

    def fetch_subfigures_from_db(
        self,
        cursor: Cursor,
        status: Optional[
            Literal[
                SubFigureStatus.NOT_PREDICTED,
                SubFigureStatus.PREDICTED,
                SubFigureStatus.GROUND_TRUTH,
            ]
        ] = None,
    ) -> List[Tuple]:
        """Fetch not predicted subfigures from db"""
        valid_status = set(item.value for item in SubFigureStatus)
        if status is not None and status not in valid_status:
            # pylint: disable=C0209:consider-using-f-string
            raise ValueError("Figure status %s is invalid" % (status))

        query = f"""
          SELECT id, uri FROM {self.schema}.figures
          WHERE fig_type={FigureType.SUBFIGURE.value}
        """
        if status is not None:
            query += f" AND status={status}"
        cursor.execute(query)
        return cursor.fetchall()

    def _fetch_ids_with_ground_truth(
        self, cursor: Cursor, data: DataFrame
    ) -> List[int]:
        all_ids = ",".join([str(el) for el in data.id.values.tolist()])
        query_valid = f"""
            SELECT id FROM {self.schema}.figures 
            WHERE id IN ({all_ids}) AND 
                  status = '{SubFigureStatus.GROUND_TRUTH.value}'
        """
        results = cursor.execute(query_valid).fetchall()
        return [el[0] for el in results]

    def _flatten_and_update(self, cursor: Cursor, data: DataFrame, update_query: str):
        """Send the update queries as repeated statements because psycopg3 does
        not have the extra_values functions available in psycopg2."""
        tuples = data[["prediction", "id"]]
        tuples = list(tuples.itertuples(index=False, name=None))
        flattened_values = [item for sublist in tuples for item in sublist]

        all_queries = update_query * len(tuples)
        query = sql.SQL(all_queries.format(*flattened_values))
        cursor.execute(query)

    def _update_db(self, cursor, data: DataFrame) -> None:
        """Update subfigures during prediction phase. If figures in the data
        already contain ground truth data, do not update its status.
        """
        # only update status for figures without ground-truth
        ids_with_gt = self._fetch_ids_with_ground_truth(cursor, data)
        df_with_gt = data.loc[data.id.isin(ids_with_gt)]
        df_without_gt = data.loc[~data.id.isin(ids_with_gt)]

        if len(df_with_gt) > 0:
            update_query1 = f"UPDATE {self.schema}.figures SET "
            update_query1 += "label=('{}') WHERE id=({}); "
            self._flatten_and_update(cursor, df_with_gt, update_query1)

        if len(df_without_gt) > 0:
            update_query2 = f"UPDATE {self.schema}.figures SET status={SubFigureStatus.PREDICTED.value},"
            update_query2 += " label=('{}') WHERE id=({}); "
            self._flatten_and_update(cursor, df_without_gt, update_query2)

    def predict_and_update_db(
        self,
        status: Optional[
            Literal[
                SubFigureStatus.NOT_PREDICTED,
                SubFigureStatus.PREDICTED,
                SubFigureStatus.GROUND_TRUTH,
            ]
        ] = None,
    ):
        """Predict label and set status to predicted"""
        # pylint: disable=not-context-manager
        with connect(conninfo=self.params.conninfo(), autocommit=False) as conn:
            output_df = None
            with conn.cursor() as cursor:
                try:
                    # tuples id, img_path
                    rows = self.fetch_subfigures_from_db(cursor, status=status)
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
