""" Module to exporting the database records for indexing """

from typing import Optional, List, Tuple
from dataclasses import asdict
from datetime import datetime
from collections import defaultdict
from pandas import json_normalize as pd_json_normalize
import psycopg
from psycopg import Cursor
from biosearch_core.data.figure import FigureType
from biosearch_core.indexing.lucene import LuceneCaption, LuceneDocument
from biosearch_core.db.model import ConnectionParams


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
                  SELECT d.id, d.repository as source_x, d.title, d.abstract, d.publication_date as publish_time, d.journal, d.authors, d.doi, d.pmcid, COUNT(f.name) as number_figures, array_agg(f.label), d.otherid
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

        # https://github.com/PyCQA/pylint/issues/5273
        # pylint: disable=not-context-manager
        with psycopg.connect(conninfo=self.params.conninfo(), autocommit=False) as conn:
            with conn.cursor() as cursor:
                document_db_records = self.get_documents_from_db(cursor)
                caption_db_records = self.get_captions_from_db(cursor)

                id_to_captions = defaultdict(list)
                for caption in caption_db_records:
                    id_to_captions[caption[0]].append(
                        LuceneCaption(figure_id=caption[1], text=caption[2])
                    )
                for document in document_db_records:
                    modalities = self._add_modality_parents(document[10])
                    captions = id_to_captions[document[0]]
                    lucene_docs.append(
                        LuceneDocument(
                            doc_id=document[0],
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
                            otherid=document[11],
                        )
                    )
        return lucene_docs

    def to_parquet(self, output_file: str) -> None:
        """save data as parquet"""
        documents_to_index = self.fetch_docs_to_index()
        data = pd_json_normalize(asdict(obj) for obj in documents_to_index)
        data.modalities = data.modalities.astype(str)
        data.to_parquet(output_file, engine="pyarrow")
