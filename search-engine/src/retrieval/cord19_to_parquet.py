""" Create a parquet file from CORD19 data for indexing
This script reads the CORD19 records from the database and process the 
documents that have image data associated. The extracted records follow the
structure described in retrieval/index.
"""

from dataclasses import asdict
import pandas as pd
from utils import simple_select
from models import LuceneDocument
from datetime import datetime
from dotenv import dotenv_values
from argparse import ArgumentParser


def get_documents(db_params: dict) -> list[tuple]:
    """Get all CORD19 documents with figures extracted"""
    query = """
              SELECT d.id, d.repository as source_x, d.title, d.abstract, d.publication_date as publish_time, d.journal, d.authors, d.doi, d.pmcid, COUNT(f.name) as number_figures
              FROM dev.documents d, dev.figures f
              WHERE d.project='cord19' and d.uri is not NULL and f.doc_id=d.id and f.fig_type=0
              GROUP BY d.id
          """
    return simple_select(db_params, query)


def get_documents_modality_info(db_params: dict) -> list[tuple]:
    """Get the modalities as an array for each document id"""

    query = """
              SELECT d.id, array_agg(l.prediction)
              FROM dev.figures as f, dev.labels_cord19 l, dev.documents d
              WHERE 
                d.project='cord19'
                AND d.uri IS NOT NULL
                AND f.doc_id = d.id
                AND f.fig_type=1 
                AND f.id = l.figure_id
                AND
                  (d.id, f.name, CHAR_LENGTH(l.prediction)) IN (
                    SELECT d2.id, f2.name, MAX(CHAR_LENGTH(l2.prediction)) max_length
                    FROM dev.figures as f2, dev.labels_cord19 as l2, dev.documents d2
                    WHERE 
                      d2.project='cord19'
                      AND d2.uri IS NOT NULL
                      AND f2.doc_id = d2.id
                      AND f2.fig_type=1 
                      AND f2.id = l2.figure_id
                    GROUP BY d2.id, f2.name
                  )
              GROUP BY d.id
            """
    return simple_select(db_params, query)


def get_documents_to_index(db_params: dict) -> list[LuceneDocument]:
    """Retrieve the cord19 metadata and the modality information. Merge the
    resulting collection on documents supported by the indexing engine.
    """
    lucene_docs = []
    document_tuples = get_documents(db_params)

    for document in document_tuples:
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
                modalities=[],
            )
        )
    modality_tuples = get_documents_modality_info(config)
    id_2_modalities = {x[0]: x[1] for x in modality_tuples}

    for document in lucene_docs:
        modalities = id_2_modalities.get(document.docId, None)
        if modalities:
            # add the parents to the modalities so we can filter by levels
            parents = [x.split(".")[0] for x in modalities if "." in x]
            modalities += parents
            document.modalities = ";".join(modalities)
    return lucene_docs


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="cord2parquet",
        description="Save cord19 data from db to parquet for indexing",
    )
    parser.add_argument("-c", "--config", type=str)
    parser.add_argument("-o", "--output", type=str)

    args = parser.parse_args()
    config = dotenv_values(args.config)

    documents_to_index = get_documents_to_index(config)
    df = pd.json_normalize(asdict(obj) for obj in documents_to_index)
    df.modalities = df.modalities.astype(str)
    df.to_parquet(args.output)
