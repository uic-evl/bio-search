""" Tests for bilava api"""
from pathlib import Path
from biosearch_core.controllers.bilava import fetch_classifiers


def test_fetch_classifiers():
    """Test that we can read the available classifiers from the definitions file"""
    project_path = Path("./tests/bilava/fake_project")
    classifiers = fetch_classifiers(str(project_path))
    assert len(classifiers) == 9
    assert "higher-modality" in classifiers
    assert "experimental" in classifiers
    assert "gel" in classifiers
    assert "graphics" in classifiers
    assert "microscopy" in classifiers
    assert "electron" in classifiers
    assert "molecular" in classifiers
    assert "radiology" in classifiers
    assert "photography" in classifiers
