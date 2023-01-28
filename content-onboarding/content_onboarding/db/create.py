""" Create needed tables on a defined schema"""

import logging
from content_onboarding.db.model import connect, ConnectionParams


def create_documents_table(db_params: ConnectionParams, schema: str, owner: str):
    """Create documents table"""
    sql = """
      -- Table: dev.documents
      -- DROP TABLE IF EXISTS {schema}.documents;

      CREATE TABLE IF NOT EXISTS {schema}.documents
      (
          id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1 ),
          title TEXT COLLATE pg_catalog."default" NOT NULL,
          abstract TEXT COLLATE pg_catalog."default",
          publication_date date,
          pmcid TEXT COLLATE pg_catalog."default",
          pubmed_id integer,
          journal TEXT COLLATE pg_catalog."default",
          repository TEXT COLLATE pg_catalog."default",
          project TEXT COLLATE pg_catalog."default" NOT NULL,
          license TEXT COLLATE pg_catalog."default",
          status TEXT COLLATE pg_catalog."default",
          uri TEXT COLLATE pg_catalog."default",
          doi TEXT COLLATE pg_catalog."default",
          notes TEXT COLLATE pg_catalog."default",
          authors TEXT[] COLLATE pg_catalog."default",
          import_date date NOT NULL,
          CONSTRAINT documents_pkey PRIMARY KEY (id)
      )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS {schema}.documents
      OWNER to {owner};
    """.format(
        schema=schema, owner=owner
    )

    try:
        conn = connect(db_params)
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
    # pylint: disable=broad-except
    except Exception as exception:
        logging.error("Failed to establish database connection\n", exc_info=True)
        raise Exception(exception) from exception
    finally:
        conn.close()
