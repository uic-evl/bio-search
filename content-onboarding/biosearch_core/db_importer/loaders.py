""" Load metadata from file"""

from os import listdir
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime
from pathlib import Path
import numpy as np
import csv
import json
import requests
from time import sleep
from biosearch_core.data.document import DbDocument

# pylint: disable=too-few-public-methods
class Loader(ABC):
    """Base abstract class for metadata loaders"""

    @abstractmethod
    def load(self, csv_path: str, pdf_paths: Dict[str, str]) -> List[DbDocument]:
        """prepare documents for database insert"""


class Cord19Loader(Loader):
    """Loader implementation for COR19"""

    def __init__(self) -> None:
        super().__init__()
        self.prefix = "PMC"
        self.folder_name = "pmcid"
        self.lookup_id = "pmcid"
        self.subfig_prefix = False

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
                    otherid=None,
                )
                documents.append(document)
        return documents


class GDXLoader(Loader):
    """Loader for the GDX2000 collection"""

    def __init__(self) -> None:
        super().__init__()
        self.prefix = None
        self.folder_name = "cord_uid"
        self.lookup_id = "otherid"
        self.subfig_prefix = True

    def get_metadata(self, pmid, gxd_entry, pubmed_dict):
        """Parse entries from our metadata and the data queried from PubMed"""

        data = pubmed_dict["result"][pmid]

        authors = [x["name"] for x in data["authors"]]
        publication_date = datetime.strptime(data["sortpubdate"][:10], "%Y/%m/%d")
        journal = data["fulljournalname"]
        import_date = datetime.now()

        pmcid = None
        doi = None
        for articleid in data["articleids"]:
            if articleid["idtype"] == "pmcid":
                pmcid = articleid["value"]
            elif articleid["idtype"] == "pmc":
                pmcid = articleid["value"]
            if articleid["idtype"] == "doi":
                doi = articleid["value"]
        uri = f"{gxd_entry['jaxid']}/{gxd_entry['jaxid']}.pdf"

        return DbDocument(
            title=gxd_entry["title"],
            abstract=gxd_entry["abstract"],
            authors=authors,
            modalities=None,
            publication_date=publication_date,
            pmcid=pmcid,
            pubmed_id=pmid,
            license=None,
            journal=journal,
            doi=doi,
            cord_uid=gxd_entry["jaxid"],
            repository="pubmed",
            uri=uri,
            status="IMPORTED",
            project="gxd",
            notes=None,
            import_date=import_date,
            otherid=gxd_entry["jaxid"],
        )

    def load(self, csv_path: str, pdf_paths: List[str]) -> List[DbDocument]:
        # TODO rename csv_path to doc_path, here is a json object

        with open(csv_path, "r", encoding="utf-8") as f_in:
            gdx = json.loads(f_in.read())
        gdx_pubmed_ids = [x["pmid"] for x in gdx]
        gdx = {x["pmid"]: x for x in gdx}

        # split to query NCBI
        n_splits = len(gdx_pubmed_ids) // 100
        id_splits = np.array_split(gdx_pubmed_ids, n_splits)

        documents = []

        for split in id_splits:
            concat_pmids = ",".join(split)
            # pylint: disable=missing-timeout
            # print(
            #     f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={concat_pmids}&retmode=json"
            # )
            res_pubmedids = requests.get(
                f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={concat_pmids}&retmode=json"
            )
            for pmid in split:
                document = self.get_metadata(pmid, gdx[pmid], res_pubmedids.json())
                documents.append(document)
            sleep(2.5)
        pdfs = {Path(el).stem for el in pdf_paths}
        # only use pdfs with jaxid from gdx2000
        print(list(pdfs)[:5])
        # print(documents[:5])
        filtered_documents = [el for el in documents if el.cord_uid in pdfs]
        return filtered_documents
