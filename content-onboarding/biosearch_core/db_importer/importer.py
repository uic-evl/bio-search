""" Module responsible for taking documents from to_import and inserting 
them in the database"""

from pathlib import Path
from os import listdir
from typing import List, Dict, Tuple
from shutil import move
import logging
import json
from psycopg import Cursor, connect
from biosearch_core.db.model import ConnectionParams
from biosearch_core.data.figure import (
    DBFigure,
    FigureStatus,
    FigureType,
    SubFigureStatus,
)
from biosearch_core.data.document import DbDocument
from biosearch_core.db_importer.bbox_reader import BoundingBoxMapper
from biosearch_core.db_importer.loaders import Loader
from biosearch_core.db_importer.project import Project
from biosearch_core.db_importer.tables import (
    create_documents_table,
    create_figures_table,
)


class Validator:
    """Validates that the folder to import has the required folder structure
    and metadata. Also, store all the folders violating the requirements by
    category"""

    def __init__(self):
        self.violation_reasons_ = {
            "to_segment": [],
            "not_in_metadata": [],
            "to_extract": [],
            "missing_pdf": [],
            "multiple_pdfs": [],
        }

    def _fetch_content(self, path: Path, extension: str) -> List[str]:
        return [str(path / elem) for elem in listdir(path) if elem.endswith(extension)]

    def _has_valid_pdfs(self, folder: Path) -> bool:
        pdfs = self._fetch_content(folder, ".pdf")

        if len(pdfs) == 0:
            logging.info("%s,MISSING_DATA", folder.name)
            self.violation_reasons_["missing_pdf"].append(str(folder))
            return False
        if len(pdfs) > 1:
            logging.info("%s,MULTIPLE_PDFS", folder.name)
            self.violation_reasons_["multiple_pdfs"].append(str(folder))
            return False
        return True

    def _has_extration_data(self, folder: Path) -> bool:
        metadata_file = f"{folder.name}.json"
        if not (folder / metadata_file).exists():
            self.violation_reasons_["to_extract"].append(str(folder))
            logging.info("%s,TO_EXTRACT,missing metadata", folder.name)
            return False
        return True

    def _has_extracted_figures(self, folder: Path) -> bool:
        metadata_file = folder / f"{folder.name}.json"
        with open(metadata_file, "r", encoding="utf-8") as reader:
            json_data = json.load(reader)
            for page in json_data["pages"]:
                for figure in page["figures"]:
                    fig_path = folder / figure["id"]
                    if not fig_path.exists():
                        self.violation_reasons_["to_extract"].append(str(folder))
                        logging.info("%s,TO_EXTRACT,image missing", folder.name)
                        return False
                    fig_folder = Path(str(fig_path)[:-4])
                    if not fig_folder.exists():
                        self.violation_reasons_["to_segment"].append(str(folder))
                        logging.info("%s,TO_SEGMENT,missing extraction folder")
                        return False
                    if not (fig_folder / f"{fig_path.name}.txt").exists():
                        self.violation_reasons_["to_segment"].append(str(folder))
                        logging.info("%s,TO_SEGMENT,missing segment data", folder.name)
                        return False
        return True

    def is_valid_folder(self, folder: str) -> bool:
        """Whether the folder has all the requirements to be imported to db"""
        folder_path = Path(folder)
        if not self._has_valid_pdfs(folder_path):
            return False
        return self._has_extration_data(folder_path) and self._has_extracted_figures(
            folder_path
        )


class ImportManager:
    """Manage document inserts to db"""

    def __init__(self, projects_dir: str, project: str, conn_params: ConnectionParams):
        self.projects_dir = Path(projects_dir)
        self.project = project
        self.dir = self.projects_dir / self.project
        self.params = conn_params
        self.validator = Validator()

        if not self.projects_dir.exists():
            raise FileNotFoundError(f"projects dir {projects_dir} does not exist")

    def _fetch_content(self, path: Path, extension: str) -> List[str]:
        return [str(path / elem) for elem in listdir(path) if elem.endswith(extension)]

    def validate_pdf_folders(self, folders: List[str]) -> Tuple[List[Path], Dict]:
        """Return folders to skip because they do not meet import requirements
        and return the constrains not met"""
        skipping = []
        for folder in folders:
            if not self.validator.is_valid_folder(folder):
                skipping.append(folder)
        return skipping

    def fetch_folder_figures(
        self, folder: Path, doc_id: int, source: str
    ) -> List[DBFigure]:
        """Read the metadata file from a PMC folder to get the figure info"""
        figures = []
        metadata_file = f"{folder.name}.json"
        with open(folder / metadata_file, "r", encoding="utf-8") as reader:
            json_data = json.load(reader)
            for page in json_data["pages"]:
                for fig_data in page["figures"]:
                    coordinates = fig_data["bbox"]
                    width = coordinates[2]
                    height = coordinates[3]

                    figures.append(
                        DBFigure(
                            status=FigureStatus.IMPORTED.value,
                            uri=f"{folder.stem}/{fig_data['id']}",
                            width=width,
                            height=height,
                            type=FigureType.FIGURE.value,
                            name=fig_data["name"],
                            caption=fig_data["caption"],
                            num_panes=0,
                            doc_id=doc_id,
                            parent_id=None,
                            coordinates=coordinates,
                            source=source,
                            page=page["number"],
                        )
                    )
        return figures

    def fetch_figures(
        self, paths_to_import: List[Path], pmc_to_id: Dict[str, str]
    ) -> Tuple[List[DBFigure], List[str]]:
        """Inspect every folder and collect figures and subfigures"""
        figures = []
        for folder in paths_to_import:
            folder_path = Path(folder)
            doc_id = pmc_to_id[folder_path.stem]
            figures += self.fetch_folder_figures(folder_path, doc_id, self.project)
        return figures

    def fetch_subfigures(
        self, figures: List[DBFigure], url_to_id: Dict[str, str]
    ) -> List[DBFigure]:
        """Fetch subfigures and bounding boxes information"""
        subfigures = []

        for figure in figures:
            figure_folder = Project.import_dir(self.dir) / figure.uri[:-4]
            subfig_paths = self._fetch_content(figure_folder, ".jpg")

            bbox_reader = BoundingBoxMapper()
            bbox_reader.load(subfig_paths)
            for subfig_path in subfig_paths:
                try:
                    coordinates = bbox_reader.mapping[subfig_path]
                    if len(coordinates) == 0:
                        # no subfigures present
                        coordinates = [0, 0, figure.width, figure.height]
                except KeyError:
                    # figsplit did not generate coordinates file
                    coordinates = None
                    message = f"Missing coordinates: {subfig_path}"
                    logging.info(message)

                local_path = Path(subfig_path)
                subfigures.append(
                    DBFigure(
                        status=SubFigureStatus.NOT_PREDICTED.value,
                        uri=f"{figure.uri[:-4]}/{local_path.name}",
                        width=coordinates[2] if coordinates else -1,
                        height=coordinates[3] if coordinates else -1,
                        type=FigureType.SUBFIGURE.value,
                        name=local_path.stem,
                        caption=None,
                        num_panes=None,
                        doc_id=figure.doc_id,
                        parent_id=url_to_id[figure.uri],
                        coordinates=coordinates,
                        source=self.project,
                        page=figure.page,
                    )
                )
                figure.num_panes += 1
        return subfigures

    def _get_paths_to_import(self):
        import_dir = Project.import_dir(self.dir)
        return [
            str(import_dir / doc)
            for doc in listdir(import_dir)
            if doc.startswith("PMC")
        ]

    def _move(self, folders: List[str], target: Path):
        for folder in folders:
            dest = target / Path(folder).name
            move(folder, dest)

    def _move_successful_imports(self, folders: List[str]):
        self._move(folders, Project.predict_dir(self.dir))

    def _move_folder_with_errors(self):
        reasons = self.validator.violation_reasons_
        self._move(reasons["to_segment"], Project.segment_dir(self.dir))
        self._move(reasons["to_extract"], Project.extract_dir(self.dir))
        self._move(reasons["not_in_metadata"], Project.error_no_meta_dir(self.dir))
        self._move(reasons["missing_pdf"], Project.error_missing_pdf_dir(self.dir))
        self._move(reasons["multiple_pdfs"], Project.error_multiple_dir(self.dir))

    def _insert_documents_to_db(self, cursor: Cursor, documents: List[DbDocument]):
        """Massive import of documents to database"""
        schema = self.params.schema
        # pylint: disable=line-too-long
        sql = f"COPY {schema}.documents (title, authors, abstract, publication_date, pmcid, pubmed_id, journal, repository, project, license, status, uri, doi, notes, import_date) FROM STDIN"
        with cursor.copy(sql) as copy:
            for doc in documents:
                copy.write_row(doc.to_tuple())

    def _insert_figures_to_db(self, cursor: Cursor, figures: List[DBFigure]):
        """Massive import of figures to database"""
        schema = self.params.schema
        # pylint: disable=line-too-long
        sql = f"COPY {schema}.figures (name,caption,num_panes,fig_type,doc_id,status,uri,parent_id,width,height,coordinates,last_update_by,owner,migration_key,notes,label,source,page) FROM STDIN"
        with cursor.copy(sql) as copy:
            for elem in figures:
                copy.write_row(elem.to_tuple())

    def _build_uri_to_id_mapper(self, cursor: Cursor) -> Dict[str, int]:
        """
        Query the database for the insert figures and create a dictionary that
        matches the figure path to the database id. We can just this match to
        populate the figure id for the labels table.
        """
        schema = self.params.schema
        query = f"select id, uri from {schema}.figures WHERE status = {FigureStatus.IMPORTED.value}"
        cursor.execute(query)
        rows = cursor.fetchall()
        return {r[1]: r[0] for r in rows}

    def _build_pmc_to_id_mapper(self, cursor: Cursor) -> Dict[str, str]:
        """Get a dictionary [pmcid, doc_id] to match figures to their corresponding
        source documents"""
        schema = self.params.schema
        sql = f"select id, pmcid from {schema}.documents where status='IMPORTED' and pmcid != ''"
        cursor.execute(sql)
        rows = cursor.fetchall()
        return {r[1]: r[0] for r in rows}

    def import_content(self, metadata_path: str, loader: Loader):
        """Insert documents, figures and subfigures to the database based
        on the documents found on /to_import folder"""

        # prepare the paths to explore
        logging.info("Starting import - validating data ######################")
        paths_to_import = self._get_paths_to_import()
        logging.info("\tAvailable paths: %d", len(paths_to_import))
        path_to_remove = self.validate_pdf_folders(paths_to_import)
        logging.info("\tInvalid file paths: %d", len(path_to_remove))
        paths_to_import = list(set(paths_to_import).difference(set(path_to_remove)))
        logging.info("\tTotal candidates %d paths", len(paths_to_import))

        logging.info("Loading documents")
        documents = loader.load(metadata_path, paths_to_import)
        logging.info("  %d documents found in metadata", len(documents))

        import_dir = Project.import_dir(self.dir)
        paths_in_metadata = [str(import_dir / doc.pmcid) for doc in documents]
        paths_to_remove = list(set(paths_to_import).difference(paths_in_metadata))
        self.validator.violation_reasons_["not_in_metadata"] = paths_to_remove
        paths_to_import = paths_in_metadata

        if len(paths_to_import) == 0:
            return

        # pylint: disable=not-context-manager
        with connect(conninfo=self.params.conninfo(), autocommit=False) as conn:
            with conn.cursor() as cursor:
                try:
                    logging.info("Inserting documents")
                    self._insert_documents_to_db(cursor, documents)
                    pmc_to_id = self._build_pmc_to_id_mapper(cursor)

                    logging.info("Inserting figures")
                    figures = self.fetch_figures(paths_to_import, pmc_to_id)
                    self._insert_figures_to_db(cursor, figures)

                    logging.info("Inserting subfigures")
                    url_to_id = self._build_uri_to_id_mapper(cursor)
                    subfigures = self.fetch_subfigures(figures, url_to_id)
                    self._insert_figures_to_db(cursor, subfigures)

                    logging.info("Moving: %d", len(paths_to_import))
                    self._move_folder_with_errors()
                    self._move_successful_imports(paths_to_import)
                    logging.info("Commiting transaction")
                    conn.commit()
                # pylint: disable=broad-except
                except Exception as exc:
                    print("Error inserting content", exc)
                    logging.error("Error inserting content", exc_info=True)
                    conn.rollback()

    def create_tables(self):
        """Create database tables"""
        # pylint: disable=not-context-manager
        with connect(conninfo=self.params.conninfo(), autocommit=False) as conn:
            with conn.cursor() as cursor:
                try:
                    schema = self.params.schema
                    owner = self.params.user
                    cursor.execute(create_documents_table(schema, owner))
                    cursor.execute(create_figures_table(schema, owner))
                # pylint: disable=broad-except
                except Exception as exc:
                    print("Erorr creating tables", exc)
                    logging.error("Error creating tables", exc_info=True)
                    conn.rollback()
