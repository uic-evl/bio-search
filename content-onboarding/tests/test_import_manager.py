""" Tests for importing folders into database 
test only this set: poetry run pytest -sv tests/test_import_manager.py
"""

import tempfile
import json
from os import makedirs
from typing import Dict
from pathlib import Path

from content_onboarding.managers.import_manager import ImportManager, Cord19Loader
from content_onboarding.db.model import FigureType, FigureStatus

# Fake data ###################################################################


def create_figure_metadata() -> Dict:
    """Fake metadata left by figure extractor"""
    return {
        "pages": [
            {
                "number": 1,
                "figures": [
                    {
                        "name": "Figure 1",
                        "caption": "some caption",
                        "id": "fig1",
                        "bbox": [0, 0, 123, 250],
                    },
                    {
                        "name": "Figure 2",
                        "caption": "some caption 2",
                        "id": "fig2",
                        "bbox": [200, 300, 123, 250],
                    },
                ],
            },
            {
                "number": 3,
                "figures": [
                    {
                        "name": "Figure 3",
                        "caption": "some caption 3",
                        "id": "fig3",
                        "bbox": [0, 0, 123, 250],
                    },
                    {
                        "name": "Figure 4",
                        "caption": "some caption 4",
                        "id": "fig4",
                        "bbox": [200, 300, 123, 250],
                    },
                ],
            },
        ]
    }


def create_fake_subfigures(folder: Path):
    """Create two fake subfigures"""
    fig_name = folder.name
    Path(folder / "001.jpg").touch()
    Path(folder / "002.jpg").touch()

    coordinates_path = folder / f"{fig_name}.jpg.txt"
    with open(coordinates_path, "w", encoding="utf-8") as out:
        out.write("   1.0e+03 *\n")
        out.write("\n")
        out.write("    0.0006    0.0221    0.9017    0.2131\n")
        out.write("    0.0314    0.8361    0.9760    0.2642\n")


def create_valid_pmc_folder(import_folder: Path, idx: int):
    """structure of a valid folder to import"""
    folder_name = import_folder / f"PMC{idx+1}"
    makedirs(folder_name, exist_ok=True)
    Path(folder_name / "document.pdf").touch()
    metadata = create_figure_metadata()

    metadata_file = f"{folder_name.name}.json"
    with open(folder_name / metadata_file, "w", encoding="utf-8") as mfile:
        serialized = json.dumps(metadata, indent=4)
        mfile.write(serialized)

    for fig_id in range(4):
        fig_folder = folder_name / f"fig{fig_id + 1}"
        Path(folder_name / f"fig{fig_id + 1}.jpg").touch()
        makedirs(fig_folder)
        create_fake_subfigures(fig_folder)


def create_invalid_pmc_folder_without_document(import_folder: Path, idx: int):
    """Simulate a folder missing pdf data"""
    folder_name = import_folder / f"PMC{idx+1}"
    makedirs(folder_name, exist_ok=True)


def create_invalid_pmc_folder_with_doc_not_extracted(import_folder: Path, idx: int):
    """Simulate a folder missing pdf data"""
    folder_name = import_folder / f"PMC{idx+1}"
    makedirs(folder_name, exist_ok=True)
    Path(folder_name / "document.pdf").touch()


def create_fake_import_folder(tmp_dir: str, project_name: str) -> Path:
    """Create 2 fake PMC folders to import"""
    root = Path(tmp_dir).resolve()
    import_folder = root / project_name / "to_import"
    makedirs(import_folder, exist_ok=True)

    for idx in range(2):
        create_valid_pmc_folder(import_folder, idx)


# Tests ######################################################################


def test_searching_on_correct_paths():
    """Test we read all the documents from dir"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        project = "cord19"
        env_file = Path("./tests/sample_data/.fakeenv")
        # csv_path = Path("./tests/sample_data/fake_cord19_metadata.csv")

        create_fake_import_folder(tmp_dir, project)
        manager = ImportManager(tmp_dir, project, str(env_file))
        # pylint: disable=protected-access
        paths = manager._get_paths_to_import()
        assert len(paths) == 2


def test_cord19_loader_populates_documents_in_disk_and_metadata():
    """Test we read metadata from cord19 csv"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        project = "cord19"
        env_file = Path("./tests/sample_data/.fakeenv")
        csv_path = Path("./tests/sample_data/fake_cord19_metadata.csv")

        create_fake_import_folder(tmp_dir, project)
        loader = Cord19Loader()

        manager = ImportManager(tmp_dir, project, str(env_file))
        # pylint: disable=protected-access
        paths = manager._get_paths_to_import()

        documents = loader.load(csv_path, paths)
        assert len(documents) == 2


# test we ignore whatever not present in cord19
def test_cord19_loader_ignores_files_not_in_metadata():
    """Test we read metadata from cord19 csv"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        project = "cord19"
        env_file = Path("./tests/sample_data/.fakeenv")
        csv_path = Path("./tests/sample_data/fake_cord19_metadata.csv")

        create_fake_import_folder(tmp_dir, project)

        # add a folder that is not in the metadata file
        import_folder = Path(tmp_dir) / project / "to_import"
        create_valid_pmc_folder(import_folder, 999)

        loader = Cord19Loader()
        manager = ImportManager(tmp_dir, project, str(env_file))
        # pylint: disable=protected-access
        paths = manager._get_paths_to_import()

        documents = loader.load(csv_path, paths)
        assert len(documents) == 2


def test_fetching_figures_and_subfigures():
    """Test we are fetching the 8 fake figures from the 2 fake PMC folders"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        project = "cord19"
        env_file = Path("./tests/sample_data/.fakeenv")

        create_fake_import_folder(tmp_dir, project)
        manager = ImportManager(tmp_dir, project, str(env_file))
        # pylint: disable=protected-access
        paths = manager._get_paths_to_import()

        pmc_to_id = {"PMC1": 1, "PMC2": 2}
        figures = manager.fetch_figures(paths, pmc_to_id)

        url_to_id = {
            "PMC1/fig1.jpg": 1,
            "PMC1/fig2.jpg": 2,
            "PMC1/fig3.jpg": 3,
            "PMC1/fig4.jpg": 4,
            "PMC2/fig1.jpg": 5,
            "PMC2/fig2.jpg": 6,
            "PMC2/fig3.jpg": 7,
            "PMC2/fig4.jpg": 8,
        }
        subfigures = manager.fetch_subfigures(figures, url_to_id)
        assert len(figures) == 8
        assert len(subfigures) == 16
        assert figures[0].type == FigureType.FIGURE
        assert subfigures[0].type == FigureType.SUBFIGURE


def test_validation_identifies_folder_to_ignore():
    """We should only process folders with complete data"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        project = "cord19"
        env_file = Path("./tests/sample_data/.fakeenv")

        create_fake_import_folder(tmp_dir, project)
        # add invalid data
        import_folder = Path(tmp_dir) / project / "to_import"
        create_invalid_pmc_folder_without_document(import_folder, 999)
        create_invalid_pmc_folder_with_doc_not_extracted(import_folder, 555)

        manager = ImportManager(tmp_dir, project, str(env_file))
        # pylint: disable=protected-access
        paths = manager._get_paths_to_import()
        invalid_folders = manager.validate_pdf_folders(paths)

        assert len(invalid_folders) == 2
