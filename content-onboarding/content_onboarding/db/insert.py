""" Module for inserting into PostgreSQL"""

import logging
from content_onboarding.db.model import connect, ConnectionParams, DbDocument


def insert_documents_to_db(db_params: ConnectionParams, documents: list[DbDocument]):
    """Massive import of documents to database"""
    try:
        conn = connect(db_params)
        with conn.cursor() as cur:
            # pylint: disable=line-too-long
            sql = f"COPY {db_params.schema}.documents (title, authors, abstract, publication_date, pmcid, pubmed_id, journal, repository, project, license, status, uri, doi, notes, import_date) FROM STDIN"
            with cur.copy(sql) as copy:
                for doc in documents:
                    copy.write_row(doc.to_tuple())
        conn.commit()
    # pylint: disable=broad-except
    except Exception as exception:
        logging.error("Failed inserting documents\n", exc_info=True)
        raise Exception(exception) from exception
    finally:
        conn.close()
