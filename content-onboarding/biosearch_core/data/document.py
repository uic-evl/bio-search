""" Document definitions"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
from psycopg import Cursor
from biosearch_core.data.figure import FigureType


class DocumentType(Enum):
    """Figure type in the database"""

    IMPORTED = "imported"


@dataclass
class DbDocument:
    """Document in database"""

    title: str
    project: str
    status: str
    import_date: datetime
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
            self.title if self.title is not None else None,
            self.authors,
            self.abstract if self.abstract is not None else None,
            self.publication_date,
            self.pmcid,
            self.pubmed_id,
            self.journal if self.journal is not None else None,
            self.repository,
            self.project,
            self.license,
            self.status,
            self.uri,
            self.doi,
            self.notes,
            self.import_date,
        )


@dataclass
class DocSurrogate:
    """Document surrogate"""

    doc_id: int
    title: str
    authors: str
    journal: str
    num_figures: int
    pmcid: str


@dataclass
class Subfigure:
    """Convenient structure for rows from query query_fig_subfigs"""

    figure_id: int
    subfigure_id: int
    caption: str
    figure_url: str
    subfigure_url: str
    coordinates: List[float]
    prediction: str
    figure_width: float
    figure_height: float
    page_number: int

    def __post_init__(self):
        if self.coordinates:
            self.coordinates = [float(x) for x in self.coordinates]


class DocumentModel:
    """Model class to fetch data from database"""

    @staticmethod
    def fetch_surrogate_details(
        cursor: Cursor, doc_id: int, schema: str
    ) -> DocSurrogate:
        """Retrieve document surrogate details"""
        query = """
            SELECT d.id, d.title, d.authors, d.journal, COUNT(f.id), d.pmcid
            FROM {schema}.documents d, {schema}.figures f
            WHERE d.id = {doc_id} 
                  AND f.doc_id = d.id 
                  AND f.fig_type = {fig_type}
        """.format(
            schema=schema, doc_id=doc_id, fig_type=FigureType.FIGURE
        )
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            return DocSurrogate(
                doc_id=rows[0][0],
                title=rows[0][1],
                authors=rows[0][2],
                journal=rows[0][3],
                num_figures=rows[0][4],
                pmcid=rows[0][5],
            )
        raise Exception(f"No data found for document {doc_id}")

    @staticmethod
    def fetch_subfigures(cursor: Cursor, doc_id: int, schema: str) -> List[Subfigure]:
        """Fetch document subfigures"""
        # TODO, captions should be fetched separately to not repeat the data
        query = """
            SELECT f.id as figId, sf.id as subfigId, f.caption, f.uri, sf.uri, sf.coordinates, sf.label as prediction, f.width, f.height, f.page
            FROM {schema}.figures f, 
                 {schema}.figures sf,
                 {schema}.documents d
            WHERE d.id={doc_id} 
                 AND d.id = f.doc_id 
                 AND f.fig_type=0  
                 AND f.id = sf.parent_id 
        """.format(
            schema=schema, doc_id=doc_id
        )
        cursor.execute(query)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append(
                Subfigure(
                    figure_id=row[0],
                    subfigure_id=row[1],
                    caption=row[2],
                    figure_url=row[3],
                    subfigure_url=row[4],
                    coordinates=row[5],
                    prediction=row[6],
                    figure_width=row[7],
                    figure_height=row[8],
                    page_number=row[9],
                )
            )
        return results
