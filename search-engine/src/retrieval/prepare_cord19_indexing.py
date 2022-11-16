""" Create a parquet file from CORD19 data for indexing
This script reads the CORD19 records from the database and process the 
documents that have image data associated. The extracted records follow the
structure described in retrieval/index.
"""

from .utils import connect, simple_select


def get_documents(db_params: dict):
    """Get all CORD19 documents with figures extracted"""
    query = """
              SELECT d.id, d.repository as source_x, d.title, d.abstract, d.publication_date as publish_time, d.journal, d.authors, d.uri as url, d.pmcid, COUNT(f.name) as number_figures
              FROM dev.documents d, dev.figures f
              WHERE d.project='cord19' and d.uri is not NULL and f.doc_id=d.id and f.fig_type=0
              GROUP BY d.id
          """
    return simple_select(db_params, query)


def get_documents_modality_info(db_params: dict):
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
