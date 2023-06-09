""" Keep the folder structure"""
from pathlib import Path


class Project:
    """Folder locations for project"""

    # pylint: disable=missing-function-docstring
    @staticmethod
    def import_dir(project_dir: Path) -> Path:
        return project_dir / "to_import"

    # pylint: disable=missing-function-docstring
    @staticmethod
    def segment_dir(project_dir: Path) -> Path:
        return project_dir / "to_segment"

    # pylint: disable=missing-function-docstring
    @staticmethod
    def extract_dir(project_dir: Path) -> Path:
        return project_dir / "to_extract"

    # pylint: disable=missing-function-docstring
    @staticmethod
    def predict_dir(project_dir: Path) -> Path:
        return project_dir / "to_predict"

    # pylint: disable=missing-function-docstring
    @staticmethod
    def error_no_meta_dir(project_dir: Path) -> Path:
        return project_dir / "errors" / "not_in_metadata"

    # pylint: disable=missing-function-docstring
    @staticmethod
    def error_multiple_dir(project_dir: Path) -> Path:
        return project_dir / "errors" / "multiple_pdfs"

    # pylint: disable=missing-function-docstring
    @staticmethod
    def error_missing_pdf_dir(project_dir: Path) -> Path:
        return project_dir / "errors" / "missing_pdf"
