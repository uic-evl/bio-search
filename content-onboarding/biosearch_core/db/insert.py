""" Module for inserting into PostgreSQL"""

from typing import List
from biosearch_core.db.model import DbDocument, DBFigure


def insert_documents_to_db(cursor, schema: str, documents: List[DbDocument]):
    """Massive import of documents to database"""

    # pylint: disable=line-too-long
    sql = f"COPY {schema}.documents (title, authors, abstract, publication_date, pmcid, pubmed_id, journal, repository, project, license, status, uri, doi, notes, import_date) FROM STDIN"
    with cursor.copy(sql) as copy:
        for doc in documents:
            copy.write_row(doc.to_tuple())


def insert_figures_to_db(cursor, schema: str, figures: List[DBFigure]):
    """Massive import of figures to database"""

    # pylint: disable=line-too-long
    sql = f"COPY {schema}.figures (name,caption,num_panes,fig_type,doc_id,status,uri,parent_id,width,height,coordinates,last_update_by,owner,migration_key,notes,label,source,page) FROM STDIN"
    with cursor.copy(sql) as copy:
        for elem in figures:
            copy.write_row(elem.to_tuple())
