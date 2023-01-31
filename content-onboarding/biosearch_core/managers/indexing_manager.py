""" Module to handle the creation of files to index"""

from dataclasses import dataclass, asdict
from typing import Optional, List, Tuple
from collections import defaultdict
from datetime import datetime
from psycopg import Cursor
import pandas as pd
from biosearch_core.db.model import FigureType, ConnectionParams, connect


@dataclass
class Caption:
    """Figure caption to index. Id to match db record if needed"""

    # pylint: disable=invalid-name
    figId: int
    text: str


@dataclass
class LuceneDocument:
    """
    datetime: str in format "%Y-%m%d" or year alone
    modalities: str with modalities separated by a white space
    """

    # pylint: disable=invalid-name
    docId: int
    source: str
    title: str
    abstract: str
    pub_date: str
    journal: str
    authors: str
    pmcid: str
    num_figures: int
    modalities: str
    url: str
    captions: Optional[List[Caption]]


class IndexManager:
    """Export the data to index"""

    def __init__(self, project: str, conn_params: ConnectionParams):
        self.params = conn_params
        self.schema = conn_params.schema
        self.project = project

    def get_documents_from_db(self, cursor: Cursor) -> List[Tuple]:
        """Get all CORD19 documents with figures extracted"""
        # TODO add status filter
        # TODO separate the query aggregation to get documents without images,
        # or see how to do a full outer with groupby
        query = """
                  SELECT d.id, d.repository as source_x, d.title, d.abstract, d.publication_date as publish_time, d.journal, d.authors, d.doi, d.pmcid, COUNT(f.name) as number_figures, array_agg(f.label)
                  FROM {schema}.documents d, {schema}.figures f
                  WHERE d.project='{project}' and d.uri is not NULL and f.doc_id=d.id and f.fig_type={fig_type}
                  GROUP BY d.id
              """.format(
            schema=self.schema,
            fig_type=FigureType.SUBFIGURE.value,
            project=self.project,
        )
        cursor.execute(query)
        return cursor.fetchall()

    def get_captions_from_db(self, cursor: Cursor) -> List[Tuple]:
        """Get captions from figures related to the document"""
        # TODO add status filter
        query = """SELECT d.id, f.id, f.caption
                   FROM {schema}.documents d, {schema}.figures f
                   WHERE d.id = f.doc_id AND f.fig_type = {fig_type} AND d.project='{project}'
        """.format(
            schema=self.schema, project=self.project, fig_type=FigureType.FIGURE.value
        )
        cursor.execute(query)
        return cursor.fetchall()

    def _add_modality_parents(
        self, modalities: Optional[List[str]]
    ) -> Optional[List[str]]:
        if not modalities:
            return None
        # TODO: check this method for more than one hierarchy, only works for two levels
        parents = [x.split(".")[0] for x in modalities if "." in x]
        modalities += parents
        return ";".join(modalities)

    def fetch_docs_to_index(self) -> List[LuceneDocument]:
        """Fetch data from db and return list of data to index"""
        lucene_docs = []

        conn = connect(self.params)
        with conn.cursor() as cursor:
            document_db_records = self.get_documents_from_db(cursor)
            caption_db_records = self.get_captions_from_db(cursor)

            id_to_captions = defaultdict(list)
            for caption in caption_db_records:
                id_to_captions[caption[0]].append(
                    Caption(figId=caption[1], text=caption[2])
                )
            for document in document_db_records:
                modalities = self._add_modality_parents(document[10])
                captions = id_to_captions[document[0]]
                lucene_docs.append(
                    LuceneDocument(
                        docId=document[0],
                        source=document[1],
                        title=document[2],
                        abstract=document[3],
                        pub_date=datetime.strftime(document[4], "%Y-%m-%d"),
                        journal=document[5],
                        authors=";".join(document[6]) if document[6] else "",
                        url=document[7],
                        pmcid=document[8],
                        num_figures=document[9],
                        modalities=modalities,
                        captions=captions,
                    )
                )
        conn.close()
        return lucene_docs

    def to_parquet(self, output_file: str):
        """save data as parquet"""
        documents_to_index = self.fetch_docs_to_index()
        data = pd.json_normalize(asdict(obj) for obj in documents_to_index)
        data.modalities = data.modalities.astype(str)
        data.to_parquet(output_file, engine="pyarrow")
