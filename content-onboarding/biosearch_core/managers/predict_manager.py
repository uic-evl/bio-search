# read from database the images with status ToPredict that are subfigures
# get the base path from to_predict
# predict on these images
# update image table
# the rest if for bi-lava but i dont need it now...

from os import cpu_count
from typing import Dict
from pathlib import Path
import traceback
import logging
from pandas import DataFrame
from torch import cuda

from image_modalities_classifier.models.predict import ModalityPredictor, RunConfig
from biosearch_core.managers.base import Structure
from biosearch_core.db.model import ConnectionParams, connect
from biosearch_core.db.select import select_subfigures_for_prediction
from biosearch_core.db.update import update_predictions_in_figures


class PredictManager:
    """Manage the predictions on NOT PREDICTED subfigures"""

    def __init__(
        self, project_dir: str, conn_params: ConnectionParams, classifiers: Dict
    ):
        self.params = conn_params
        device = "cuda:0" if cuda.is_available() else "cpu"
        self.run_config = RunConfig(
            batch_size=128, num_workers=cpu_count(), device=device
        )
        self.classifiers = classifiers
        self.base_img_path = Path(project_dir) / Structure.TO_PREDICT.value

    def _update_db(self, cursor, data: DataFrame):
        values = data[["prediction", "id"]]
        values = list(values.itertuples(index=False, name=None))
        flattened = [item for sublist in values for item in sublist]
        update_predictions_in_figures(cursor, self.params.schema, flattened)

    def predict(self):
        """Predict label and set status to predicted"""
        conn = connect(self.params)
        output_df = None
        with conn.cursor() as cursor:
            try:
                # tuples id, img_path
                rows = select_subfigures_for_prediction(cursor, self.params.schema)
                if len(rows) > 0:
                    rel_img_paths = [elem[1] for elem in rows]

                    predictor = ModalityPredictor(self.classifiers, self.run_config)
                    # predict does not shuffle
                    output_df = predictor.predict(rel_img_paths, self.base_img_path)
                    output_df["id"] = [elem[0] for elem in rows]
                    self._update_db(cursor, output_df)
                    conn.commit()
            except:
                logging.error("Prediction error", exc_info=True)
                traceback.print_exc()
        conn.close()
        return output_df
