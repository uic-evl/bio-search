""" Test set fo training image classifiers"""

import tempfile
from os import makedirs
from pathlib import Path
import pandas as pd
from image_modalities_classifier.models.train import ModalityModelTrainer


def test_check_artifacts_first_time():
    """Test the artifact folder data when it's the first classier version to train"""
    taxonomy = "test_taxonomy"
    classifier = "test_classifier"
    project = "test"
    with tempfile.TemporaryDirectory() as tmpdirname:
        artifacts_dir = Path(tmpdirname)

        trainer = ModalityModelTrainer(
            "./notimportant_path.parquet",
            "./notimportant_images_path",
            output_dir=artifacts_dir,
            taxonomy=taxonomy,
            classifier_name=classifier,
            project=project,
        )

        # pylint: disable=protected-access
        trainer._create_artifacts_folder()
        expected_path = Path(artifacts_dir) / taxonomy / classifier
        assert expected_path.exists()
        assert expected_path == trainer.output_dir
        assert trainer.version == 1


def test_check_artifacts_following_times():
    """Test that the trainer gets the right version for the model to update"""
    taxonomy = "test_taxonomy"
    classifier = "test_classifier"
    project = "test"
    with tempfile.TemporaryDirectory() as tmpdirname:
        artifacts_dir = Path(tmpdirname)
        # prepare existing data as if one model has been saved before
        output_dir = artifacts_dir / taxonomy / classifier
        makedirs(output_dir, exist_ok=True)
        fake_weights_file = output_dir / "test_classifier_1.pt"
        Path(fake_weights_file).touch()

        trainer = ModalityModelTrainer(
            "./notimportant_path.parquet",
            "./notimportant_images_path",
            output_dir=artifacts_dir,
            taxonomy=taxonomy,
            classifier_name=classifier,
            project=project,
        )

        # pylint: disable=protected-access
        trainer._create_artifacts_folder()
        expected_path = Path(artifacts_dir) / taxonomy / classifier
        assert expected_path == trainer.output_dir
        assert expected_path == trainer.output_dir
        assert trainer.version == 2


def test_encode_dataset():
    """Test that the trainer is encoding the input dataframe from string to ints
    Sample dataset has two columns: img_path and labels, with values:
        img_paths = ["test_1.png", "test_2.png", "test_3.png", "test_4.png"]
        labels = ["A", "B", "B", "C"]
    """
    data_path = str(Path("./tests/sample_data/sample.parquet").resolve())
    taxonomy = "test_taxonomy"
    classifier = "test_classifier"
    project = "test"

    trainer = ModalityModelTrainer(
        data_path,
        "./notimportant_images_path",
        output_dir="./notimportant_outputdir",
        taxonomy=taxonomy,
        classifier_name=classifier,
        project=project,
        remove_small=False,  # avoid removal for testing
    )
    # pylint: disable=protected-access
    trainer._prepare_data()

    assert len(trainer.encoder.classes_) == 3
    assert "enc_label" in trainer.data.columns
    assert trainer.data.enc_label.unique().tolist() == [0, 1, 2]
