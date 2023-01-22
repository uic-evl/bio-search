""" Test set fo training image classifiers"""

import tempfile
from os import makedirs
from pathlib import Path
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
