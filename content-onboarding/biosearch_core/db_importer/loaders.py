""" Load metadata from file"""

from os import listdir
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime
from pathlib import Path
import csv
from biosearch_core.data.document import DbDocument

# pylint: disable=too-few-public-methods
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

    def load(self, csv_path: str, pdf_paths: List[str]) -> List[DbDocument]:
        """Collect metadata from metadata.csv document in CORD19 collection.
        The loader insert the metadata from the documents in the database only
        if the document exists in the pdf_paths. In other words, we insert
        documents that also have extracted content.
        """
        dict_paths = {Path(elem_path).stem: elem_path for elem_path in pdf_paths}
        documents = []
        import_date = datetime.now()

        with open(csv_path, encoding="utf-8") as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                # only insert documents with local folder
                if row["pmcid"] not in dict_paths:
                    continue

                main_pdf = [
                    x for x in listdir(dict_paths[row["pmcid"]]) if x.endswith(".pdf")
                ][0]

                publication_date = self._read_publication_date(row)
                uri = f'{row["pmcid"]}/{main_pdf}'
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
