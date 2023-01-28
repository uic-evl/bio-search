""" Module responsible for taking documents from to_import and inserting 
them in the database"""

from os import listdir
from typing import List, Dict
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
import csv
import logging
import json
from content_onboarding.db.model import (
    params_from_env,
    DbDocument,
    DBFigure,
    FigureType,
    FigureStatus,
)
from content_onboarding.db.select import build_pmc_to_id_mapper
from content_onboarding.db.insert import insert_documents_to_db


class Loader(ABC):
    """Base abstract class for metadata loaders"""

    @abstractmethod
    def load(self, csv_path: str, pdf_paths: Dict[str, str]) -> List[DbDocument]:
        """prepare documents for database insert"""


class Cord19Loader(Loader):
    """Loader implementation for COR19"""

    def _read_publication_date(self, row):
        # publish time can be empty or be a YYYY-MM-DD or YYYY
        if len(row["publish_time"]) == 0:
            publication_date = None
        elif len(row["publish_time"]) == 4:
            publication_date = datetime(int(row["publish_time"]), 1, 1)
        else:
            publication_date = datetime.strptime(row["publish_time"], "%Y-%m-%d")
        return publication_date

    def _read_authors(self, row):
        # some values have NUL characters
        authors = row["authors"].split("; ")
        if len(authors[0]) == 0:
            authors = None
        else:
            for author in authors:
                author = author.replace("\x00", "")
        return authors

    def load(self, csv_path: str, pdf_paths: Dict[str, str]) -> List[DbDocument]:
        """Collect metadata from metadata.csv document in CORD19 collection.
        The loader insert the metadata from the documents in the database only
        if the document exists in the pdf_paths. In other words, we insert
        documents that also have extracted content.
        """
        documents = []
        import_date = datetime.now()

        with open(csv_path, encoding="utf-8") as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                # only insert documents with local folder
                if row["pmcid"] not in pdf_paths:
                    continue

                publication_date = self._read_publication_date(row)
                uri = pdf_paths[row["pmcid"]]
                authors = self._read_authors(row)
                # pubmed_id should be an integer value
                pubmed_id = row["pubmed_id"]
                pubmed_id = int(pubmed_id) if pubmed_id.isdecimal() else None

                document = DbDocument(
                    title=row["title"],
                    abstract=row["abstract"],
                    authors=authors,
                    modalities=None,
                    publication_date=publication_date,
                    pmcid=row["pmcid"],
                    pubmed_id=pubmed_id,
                    license=row["license"],
                    journal=row["journal"],
                    doi=row["doi"],
                    cord_uid=row["cord_uid"],
                    repository=row["source_x"],
                    uri=uri,
                    status="IMPORTED",
                    project="cord19",
                    notes=None,
                    import_date=import_date,
                )
                documents.append(document)
            return documents


class ImportManager:
    """Manage document inserts to db"""

    def __init__(self, projects_dir: str, project: str, params_file: str):
        self.projects_dir = Path(projects_dir)
        self.project = project
        self.params = params_from_env(str(Path(params_file.resolve())))

        if not self.projects_dir.exists():
            raise FileNotFoundError(f"projects dir {projects_dir} does not exist")

    def _fetch_content(self, path: Path, extension: str) -> List[str]:
        return [path / elem for elem in listdir(path) if elem.endswith(extension)]

    def _should_skip(self, folder: Path) -> bool:
        """Check if all PDFs have associated folders for images"""
        pdfs = self._fetch_content(folder, ".pdf")
        skip = False
        for pdf in pdfs:
            pdf_folder = folder / pdf
            if not pdf_folder.exists():
                skip = True
                break
        return skip

    def validate_pdf_folders(self, paths_to_import: List[Path]) -> List[Path]:
        """Folders that need to be removed because they do not have a
        corresponding folder for each PDF document
        """
        skipping = []
        for folder in paths_to_import:
            if self._should_skip(folder):
                skipping.append(folder)
        return skipping

    def fetch_folder_figures(
        self, folder: Path, doc_id: int, source: str
    ) -> List[DBFigure]:
        """Read the metadata file from a PMC folder to get the figure info"""
        figures = []
        with open(folder / "metadata.json", "r", encoding="utf-8") as reader:
            json_data = json.loads(reader)
            for page in json_data["pages"]:
                for fig_data in page["figures"]:
                    coordinates = fig_data["bbox"]
                    width = coordinates[2]
                    height = coordinates[3]

                    figures.append(
                        DBFigure(
                            id=None,
                            status=FigureStatus.STATUS_UNLABELED,
                            uri=f"{folder.stem}/{fig_data['id']}",
                            width=width,
                            height=height,
                            type=FigureType.FIGURE,
                            name=fig_data["name"],
                            caption=fig_data["caption"],
                            num_panes=None,
                            doc_id=doc_id,
                            parent_id=None,
                            coordinates=fig_data["coordinates"],
                            last_update_by=None,
                            owner=None,
                            migration_key=None,
                            notes=None,
                            labels=None,
                            source=source,
                            page=page["number"],
                        )
                    )
        return figures

    def fetch_figures(self, paths_to_import: List[Path], pmc_to_id: Dict[str, str]):
        """Inspect every folder and collect figures and subfigures"""
        figures = []
        for folder in paths_to_import:
            doc_id = pmc_to_id[folder.stem]
            figures += self.fetch_folder_figures(folder, doc_id, self.project)
        return figures

    def import_content(self, metadata_path: str, loader: Loader):
        """Insert documents, figures and subfigures to the database based
        on the documents found on /to_import folder"""
        import_dir = self.projects_dir / self.project / "to_import"
        paths_to_import = [
            str(import_dir / doc)
            for doc in listdir(import_dir)
            if doc.startswith("PMC")
        ]
        documents = loader.load(metadata_path, paths_to_import)
        # TODO -> validate folder has images
        # load images, filter skip

        insert_documents_to_db(self.params, documents)

        pmc_to_id = build_pmc_to_id_mapper(self.params)
        figures = self.fetch_figures(paths_to_import, pmc_to_id)
        # insert figures to db
        # TODO add scripts for creating tables

        # fetch mapper for subfigures
        # fetch subfigures and read coordinates
        # insert to db
