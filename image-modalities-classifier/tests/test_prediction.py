""" Inference tests """

from pathlib import Path
from os import listdir
import pandas as pd
from image_modalities_classifier.models.predict import (
    SingleModalityPredictor,
    RunConfig,
)


def test_prediction():
    """Test a prediction on two samples"""
    model_path = Path.home() / "Documents/modality_classifiers/models/microscopy_1.pt"
    base_img_dir = str(Path("./tests/sample_data").resolve())
    img_paths = listdir(base_img_dir)
    input_df = pd.DataFrame(img_paths, columns=["path"])

    config = RunConfig(batch_size=32, num_workers=1, device="cuda:0")
    predictor = SingleModalityPredictor(model_path, config)
    predictions = predictor.predict(input_df, base_img_dir)
    predictor.free()

    print(predictions)
    assert len(predictions) == 2
