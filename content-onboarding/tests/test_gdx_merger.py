""" Test cases for importing GDX content"""
from biosearch_core.preprocessing.merge_gdx import (
    fill_missing_subfigures,
    fill_coordinates,
)


def test_filling_null_subfigures():
    """Test we can process missing subfigures in raw data"""
    values = ["10_1_001.jpg", "10_1_006.jpg"]
    subfigures = fill_missing_subfigures(values)
    assert len(subfigures) == 6
    assert subfigures[0] is not None
    assert subfigures[1] is None
    assert subfigures[2] is None
    assert subfigures[3] is None
    assert subfigures[4] is None
    assert subfigures[5] is not None


def test_filling_subfigures():
    """Test we can process complete subfigures in raw data"""
    values = ["10_1_001.jpg", "10_1_002.jpg", "10_1_003.jpg"]
    subfigures = fill_missing_subfigures(values)
    assert len(subfigures) == 3
    assert subfigures[0] is not None
    assert subfigures[1] is not None
    assert subfigures[2] is not None


def test_fill_incomplete_coordinates():
    """Test grabbing coordinates for subfigures with nulls"""
    values = ["10_1_001.jpg", "10_1_006.jpg"]
    subfigures = fill_missing_subfigures(values)
    keys_to_coords = {"001": [10, 20, 30, 40], "006": [40, 50, 60, 60]}
    empty = [0, 0, 0, 0]
    coordinates = fill_coordinates(subfigures, keys_to_coords)

    assert len(coordinates) == len(subfigures)
    assert coordinates[0] == [10, 20, 30, 40]
    assert coordinates[1] == empty
    assert coordinates[2] == empty
    assert coordinates[3] == empty
    assert coordinates[4] == empty
    assert coordinates[5] == [40, 50, 60, 60]
