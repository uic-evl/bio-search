""" Test set fo training image classifiers

Sample parquet

img_path	label	is_gt	split_set
0	test_1.png	A	True	TRAIN
1	test_2.png	B	True	TRAIN
2	test_3.png	B	False	TRAIN
3	test_4.png	C	True	TRAIN
"""

import tempfile
from os import makedirs
from pathlib import Path
import pandas as pd
from image_modalities_classifier.models.trainer import ModalityModelTrainer
from image_modalities_classifier.train import parse_args


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
    Test dataset: sample.parquet
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


def test_prepare_dataset_with_pseudolabels():
    """Check pseudo labels are part of the data"""
    data_path = str(Path("./tests/sample_data/sample.parquet").resolve())
    taxonomy = "test_taxonomy"
    classifier = "test_classifier"
    project = "test"

    expected_df = pd.read_parquet(data_path)

    trainer = ModalityModelTrainer(
        data_path,
        "./notimportant_images_path",
        output_dir="./notimportant_outputdir",
        taxonomy=taxonomy,
        classifier_name=classifier,
        project=project,
        remove_small=False,  # avoid removal for testing
        use_pseudo=True,
    )
    # pylint: disable=protected-access
    trainer._prepare_data()

    assert expected_df.shape[0] == trainer.data.shape[0]
    assert expected_df.shape[1] + 1 == trainer.data.shape[1]


def test_prepare_dataset_without_pseudolabels():
    """Check pseudo labels are part of the data"""
    data_path = str(Path("./tests/sample_data/sample.parquet").resolve())
    taxonomy = "test_taxonomy"
    classifier = "test_classifier"
    project = "test"

    expected_df = pd.read_parquet(data_path)
    expected_df = expected_df.loc[
        (expected_df.split_set == "TRAIN") & (expected_df.is_gt)
    ]

    trainer = ModalityModelTrainer(
        data_path,
        "./notimportant_images_path",
        output_dir="./notimportant_outputdir",
        taxonomy=taxonomy,
        classifier_name=classifier,
        project=project,
        remove_small=False,  # avoid removal for testing
        use_pseudo=False,
    )
    # pylint: disable=protected-access
    trainer._prepare_data()

    assert expected_df.shape[0] == trainer.data.shape[0]
    assert expected_df.shape[1] + 1 == trainer.data.shape[1]


def test_parser_with_mean_and_std():
    """Test the parser passes the mean and std correctly"""
    args = [
        "classifier_name",
        "model_name",
        "model_dir",
        "data_dir",
        "-m",
        "0.1",
        "0.2",
        "0.3",
        "-s",
        "0.5",
        "0.6",
        "0.7",
    ]
    parsed_args = parse_args(args)
    assert parsed_args.mean == [0.1, 0.2, 0.3]
    assert parsed_args.std == [0.5, 0.6, 0.7]


def test_parser_without_mean_and_std():
    """Test the parser passes the mean and std correctly"""
    args = [
        "classifier_name",
        "model_name",
        "model_dir",
        "data_dir",
    ]
    parsed_args = parse_args(args)
    assert parsed_args.mean is None
    assert parsed_args.std is None
