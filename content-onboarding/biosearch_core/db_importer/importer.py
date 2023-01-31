from pathlib import Path
from os import listdir
from typing import List, Dict, Tuple
from shutil import move
import logging
import json
from biosearch_core.db.model import ConnectionParams
from biosearch_core.managers.base import Structure


## Finish refactoring
## create validator


class ImportManager:
    """Manage document inserts to db"""

    def __init__(self, projects_dir: str, project: str, conn_params: ConnectionParams):
        self.projects_dir = Path(projects_dir)
        self.project = project
        self.params = conn_params

        self.import_dir = self.projects_dir / self.project / Structure.TO_IMPORT.value
        self.pred_dir = self.projects_dir / self.project / Structure.TO_PREDICT.value
        self.segment_dir = self.projects_dir / self.project / Structure.TO_SEGMENT.value
        self.extract_dir = self.projects_dir / self.project / Structure.TO_EXTRACT.value
        self.no_meta_dir = (
            self.projects_dir
            / self.project
            / Structure.ERRORS.value
            / Structure.NO_METADATA.value
        )
        self.multiple_dir = (
            self.projects_dir
            / self.project
            / Structure.ERRORS.value
            / Structure.MULTIPLE_PDFS.value
        )
        self.missing_dir = (
            self.projects_dir
            / self.project
            / Structure.ERRORS.value
            / Structure.NO_PDFS.value
        )

        if not self.projects_dir.exists():
            raise FileNotFoundError(f"projects dir {projects_dir} does not exist")

    def _fetch_content(self, path: Path, extension: str) -> List[str]:
        return [str(path / elem) for elem in listdir(path) if elem.endswith(extension)]

    def _should_skip(self, folder: Path, reason: Dict) -> bool:
        """Check if all PDFs have associated folders for images"""
        pdfs = self._fetch_content(folder, ".pdf")

        if len(pdfs) == 0:
            logging.info("%s,MISSING_DATA", folder.name)
            reason["missing_pdf"].append(str(folder))
            return True

        if len(pdfs) > 1:
            logging.info("%s,MULTIPLE_PDFS", folder.name)
            reason["multiple_pdfs"].append(str(folder))
            return True

        if not self._is_metadata_missing(folder, reason):
            return not self._figures_in_metadata_exist(folder, reason)
        return True

    def _figures_in_metadata_exist(self, folder: Path, reason: Dict) -> bool:
        metadata_file = folder / f"{folder.name}.json"
        with open(metadata_file, "r", encoding="utf-8") as reader:
            json_data = json.load(reader)
            for page in json_data["pages"]:
                for figure in page["figures"]:
                    fig_path = folder / figure["id"]
                    if not fig_path.exists():
                        reason["to_extract"].append(str(folder))
                        logging.info("%s,TO_EXTRACT,image missing", folder.name)
                        return False
                    fig_folder = Path(str(fig_path)[:-4])
                    if not fig_folder.exists():
                        reason["to_segment"].append(str(folder))
                        logging.info("%s,TO_SEGMENT,missing extraction folder")
                        return False
                    if not (fig_folder / f"{fig_path.name}.txt").exists():
                        reason["to_segment"].append(str(folder))
                        logging.info(
                            "%s,TO_SEGMENT,missing segmentation data", folder.name
                        )
                        return False

        return True

    def _is_metadata_missing(self, folder: Path, reason: Dict) -> bool:
        metadata_file = f"{folder.name}.json"
        if not (folder / metadata_file).exists():
            reason["to_extract"].append(str(folder))
            logging.info("%s,TO_EXTRACT,missing metadata", folder.name)
            return True
        return False

    def validate_pdf_folders(
        self, paths_to_import: List[str]
    ) -> Tuple[List[Path], Dict]:
        """Folders that need to be removed because they do not have a
        corresponding folder for each PDF document
        """
        skipping = []
        reason = {
            "to_segment": [],
            "not_in_metadata": [],
            "to_extract": [],
            "missing_pdf": [],
            "multiple_pdfs": [],
        }
        for folder in paths_to_import:
            if self._should_skip(Path(folder), reason):
                skipping.append(folder)
        return skipping, reason

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
                            id=None,
                            status=FigureStatus.IMPORTED.value,
                            uri=f"{folder.stem}/{fig_data['id']}",
                            width=width,
                            height=height,
                            type=FigureType.FIGURE.value,
                            name=fig_data["name"],
                            caption=fig_data["caption"],
                            num_panes=None,
                            doc_id=doc_id,
                            parent_id=None,
                            coordinates=coordinates,
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

    def fetch_figures(
        self, paths_to_import: List[Path], pmc_to_id: Dict[str, str]
    ) -> Tuple[List[DBFigure], List[str]]:
        """Inspect every folder and collect figures and subfigures"""
        figures = []
        skipped_docs = []
        for folder in paths_to_import:
            folder_path = Path(folder)

            doc_id = pmc_to_id[folder_path.stem]
            figures += self.fetch_folder_figures(folder_path, doc_id, self.project)

        # TODO: remove skipped docs
        return figures, skipped_docs

    def fetch_subfigures(
        self, figures: List[DBFigure], url_to_id: Dict[str, str]
    ) -> List[DBFigure]:
        """Fetch subfigures and bounding boxes information"""
        subfigures = []

        for figure in figures:
            # TODO: fix test case
            figure_folder = self.import_dir / figure.uri[:-4]  # remove .jpg
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
                        id=None,
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
                        last_update_by=None,
                        owner=None,
                        migration_key=None,
                        notes=None,
                        labels=None,
                        source=self.project,
                        page=figure.page,
                    )
                )
        return subfigures

    def _get_paths_to_import(self):
        return [
            str(self.import_dir / doc)
            for doc in listdir(self.import_dir)
            if doc.startswith("PMC")
        ]

    def _move_folders(self, folders: List[str], target: Path):
        for folder in folders:
            dest = target / Path(folder).name
            move(folder, dest)

    def _move_folders_by_reason(self, reason: Dict):
        self._move_folders(reason["to_predict"], self.pred_dir)
        self._move_folders(reason["to_segment"], self.segment_dir)
        self._move_folders(reason["to_extract"], self.extract_dir)
        self._move_folders(reason["not_in_metadata"], self.no_meta_dir)
        self._move_folders(reason["missing_pdf"], self.missing_dir)
        self._move_folders(reason["multiple_pdfs"], self.multiple_dir)

    def import_content(self, metadata_path: str, loader: Loader):
        """Insert documents, figures and subfigures to the database based
        on the documents found on /to_import folder"""

        # prepare the paths to explore
        logging.info("Starting import - validating data ######################")
        paths_to_import = self._get_paths_to_import()
        logging.info("\tAvailable paths: %d", len(paths_to_import))
        path_to_remove, reason = self.validate_pdf_folders(paths_to_import)
        logging.info("\tInvalid file paths: %d", len(path_to_remove))
        paths_to_import = list(set(paths_to_import).difference(set(path_to_remove)))
        logging.info("\tTotal candidates %d paths", len(paths_to_import))

        logging.info("Loading documents")
        documents = loader.load(metadata_path, paths_to_import)
        logging.info("  %d documents found in metadata", len(documents))
        paths_in_metadata = [str(self.import_dir / doc.pmcid) for doc in documents]
        paths_to_remove = list(set(paths_to_import).difference(paths_in_metadata))
        reason["not_in_metadata"] = paths_to_remove
        paths_to_import = paths_in_metadata

        if len(paths_to_import) == 0:
            return

        conn = connect(self.params)
        schema = self.params.schema
        with conn.cursor() as cursor:
            try:
                logging.info("Inserting documents")
                insert_documents_to_db(cursor, schema, documents)
                pmc_to_id = build_pmc_to_id_mapper(cursor, schema)

                logging.info("Inserting figures")
                figures, skipped_docs = self.fetch_figures(paths_to_import, pmc_to_id)
                insert_figures_to_db(cursor, schema, figures)

                logging.info("Inserting subfigures")
                url_to_id = build_uri_to_id_mapper(cursor, schema)
                subfigures = self.fetch_subfigures(figures, url_to_id)
                insert_figures_to_db(cursor, schema, subfigures)

                # avoid folders where no parent id was found
                logging.info("Paths with errors: %d", len(skipped_docs))
                paths_to_import = list(
                    set(paths_to_import).difference(set(skipped_docs))
                )
                logging.info("Moving: %d", len(paths_to_import))

                reason["to_predict"] = paths_to_import
                self._move_folders_by_reason(reason)
                logging.info("Commiting transaction")
                conn.commit()
            # pylint: disable=broad-except
            except Exception as exc:
                print("Error inserting content", exc)
                logging.error("Error inserting content", exc_info=True)
                conn.rollback()
        conn.close()

    def create_tables(self):
        """Create database tables"""
        conn = connect(self.params)
        schema = self.params.schema
        with conn.transaction() as trx:
            try:
                create_documents_table(conn, schema, self.params.user)
                create_figures_table(conn, schema, self.params.user)
            # pylint: disable=broad-except
            except Exception as exc:
                print("Erorr creating tables", exc)
                logging.error("Error creating tables", exc_info=True)
                Rollback(trx)
        conn.close()
