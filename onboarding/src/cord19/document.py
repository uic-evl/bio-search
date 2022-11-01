from dataclasses import dataclass
from datetime import datetime
from dataclasses import field
from time import sleep
from typing import Optional
from pathlib import Path
from utils import connect
from os import listdir, path
import csv
import requests


@dataclass
class Cord19Document:
    title: str
    project: str
    status: str
    abstract: Optional[str] = field(default=None)
    authors: Optional[list[str]] = field(default=None)
    publication_date: Optional[datetime] = field(default=None)
    modalities: Optional[list[str]] = field(default=None)
    pmcid: Optional[str] = field(default=None)
    pubmed_id: Optional[int] = field(default=None)
    journal: Optional[str] = field(default=None)
    repository: Optional[str] = field(default=None)
    cord_uid: Optional[str] = field(default=None)
    license: Optional[str] = field(default=None)
    uri: Optional[str] = field(default=None)
    doi: Optional[str] = field(default=None)
    notes: Optional[str] = field(default=None)

    def to_tuple(self):
        """Return data as tuple to insert in database"""
        return (
            self.title[:200] if self.title is not None else None,
            [x[:100] for x in self.authors] if self.authors is not None else None,
            self.abstract[:2000] if self.abstract is not None else None,
            self.publication_date,
            self.pmcid,
            self.pubmed_id,
            self.journal[:100] if self.journal is not None else None,
            self.repository,
            self.project,
            self.license,
            self.status,
            self.uri,
            self.doi,
            self.notes,
        )


def load_from_cord(
    metadata_path: Path, pdf_paths: dict[str, str]
) -> list[Cord19Document]:
    """
    Collects the metadata from the CORD19 and merges the URIs with the PDFs that we
    have already processed from that collection (around 32k from the 200k)
    """
    documents = []

    with open(metadata_path) as f_in:
        reader = csv.DictReader(f_in)

        for row in reader:
            # publish time can be empty or be a YYYY-MM-DD or YYYY
            if len(row["publish_time"]) == 0:
                publication_date = None
            elif len(row["publish_time"]) == 4:
                publication_date = datetime(int(row["publish_time"]), 1, 1)
            else:
                publication_date = datetime.strptime(row["publish_time"], "%Y-%m-%d")

            # check if we have a local copy of the PDF somewhere
            uri = None
            # uic preprocessing used pmcid for folders names
            if row["pmcid"] in pdf_paths:
                uri = pdf_paths[row["pmcid"]]
            elif row["cord_uid"] in pdf_paths:
                uri = pdf_paths[row["cord_uid"]]

            # pubmed_id should be an integer value
            pubmed_id = int(row["pubmed_id"]) if row["pubmed_id"].isdecimal() else None

            # some values have NUL characters
            authors = row["authors"].split("; ")
            if len(authors[0]) == 0:
                authors = None
            else:
                for author in authors:
                    author = author.replace("\x00", "")

            document = Cord19Document(
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
            )
            documents.append(document)
        return documents


def insert_documents_to_db(db_params: dict, documents: list[Cord19Document]):
    try:
        conn = connect(**db_params)
        with conn.cursor() as cur:
            with cur.copy(
                "COPY dev.documents (title, authors, abstract, publication_date, pmcid, pubmed_id, journal, repository, project, license, status, uri, doi, notes) FROM STDIN"
            ) as copy:
                for d in documents:
                    copy.write_row(d.to_tuple())
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()


def get_metadata(id: str, uri: str, dictionary: dict, is_pmc: bool):
    """
    Our records from tinman only have either a pmcid or pmid for some documents,
    so here we extract some metadata to match the cord19 records by using
    the results from queries to pubmed that we store in dictionary.
    TODO: the queries do not return the abstracts
    """
    data = dictionary["result"][id]
    authors = [x["name"] for x in data["authors"]]
    try:
        publication_date = datetime.strptime(data["epubdate"], "%Y %b %d")
    except:
        try:
            publication_date = datetime.strptime(data["pubdate"], "%Y %b")
        except:
            publication_date = datetime.strptime(data["pubdate"], "%Y %b %d")
    journal = data["fulljournalname"]
    title = data["title"]

    pubmed_id = None
    pmcid = None
    doi = None
    for articleid in data["articleids"]:
        if articleid["idtype"] == "pmid":
            pubmed_id = articleid["value"]
        if is_pmc:
            if articleid["idtype"] == "pmcid":
                pmcid = articleid["value"]
        else:
            if articleid["idtype"] == "pmc":
                pmcid = articleid["value"]
        if articleid["idtype"] == "doi":
            doi = articleid["value"]
    project = "animo"
    license = None
    uri = uri

    return {
        "authors": authors,
        "publication_date": publication_date,
        "journal": journal,
        "title": title,
        "abstract": None,
        "project": project,
        "license": license,
        "uri": str(uri),
        "pmcid": pmcid,
        "pubmed_id": pubmed_id,
        "doi": doi,
        "cord_uid": None,
        "notes": None,
        "status": "IMPORTED",
        "modalities": None,
    }


def load_from_tinman(tinman_base_path: str) -> list[Cord19Document]:
    """
    Collect the documents from tinman and look for the metadata in pubmed.
    """
    tinman_base_path = Path(tinman_base_path)
    tinman_folders = [
        x for x in listdir(tinman_base_path) if path.isdir(tinman_base_path / x)
    ]
    tinman_docs = [str(Path("tinman") / x / x[1:]) + ".pdf" for x in tinman_folders]

    pubmed_ids = []
    pubmed_paths = []
    pmcids = []
    pmcs_paths = []
    others = []
    other_paths = []

    for doc in tinman_docs:
        doc_path = Path(doc)
        doc_name = doc_path.name[:-4]
        if "PMC" in doc_name:
            pmcids.append(doc_name[3:])  # code to query does not includes PMC prefix
            pmcs_paths.append(doc_path)
        elif len(doc_name) == 8:
            pubmed_ids.append(doc_name)
            pubmed_paths.append(doc_path)
        else:
            others.append(doc_name)
            other_paths.append(doc_path)

    concat_pubmed_ids = ",".join(pubmed_ids)
    concat_pmcids = ",".join(pmcids)
    res_pubmedids = requests.get(
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={concat_pubmed_ids}&retmode=json"
    )
    sleep(3)
    res_pmcids = requests.get(
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id={concat_pmcids}&retmode=json"
    )

    dict_pubmed = res_pubmedids.json()
    dict_pmc = res_pmcids.json()

    documents = []
    for id, doc_path in zip(pubmed_ids, pubmed_paths):
        try:
            metadata = get_metadata(id, doc_path, dict_pubmed, False)
            document = Cord19Document(**metadata)
            if document.pmcid is not None:
                document.pmcid = document.pmcid[3:]
            documents.append(document)
        except Exception as e:
            print(id)
            raise e

    for id, doc_path in zip(pmcids, pmcs_paths):
        metadata = get_metadata(id, doc_path, dict_pmc, True)
        metadata["pmcid"] = int(metadata["pmcid"][3:])
        document = Cord19Document(**metadata)
        documents.append(document)

    for id, doc_path in zip(others, other_paths):
        document = Cord19Document(
            abstract=None,
            authors=None,
            journal=None,
            title=id,
            cord_uid=None,
            doi=None,
            license=None,
            modalities=None,
            notes=None,
            pmcid=None,
            publication_date=None,
            project="animo",
            pubmed_id=None,
            repository=None,
            uri=str(doc_path),
            status="IMPORTED",
        )
        documents.append(document)
    return documents
