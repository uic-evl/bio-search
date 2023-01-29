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


def create_figures_table(db_params: ConnectionParams, schema: str, owner: str):
    """Create figures table"""
    sql = """
        -- Table: {schema}.figures
        -- DROP TABLE IF EXISTS {schema}.figures;

        CREATE TABLE IF NOT EXISTS {schema}.figures
        (
            id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1 ),
            name TEXT COLLATE pg_catalog."default",
            caption TEXT COLLATE pg_catalog."default",
            num_panes integer,
            fig_type integer,
            doc_id integer,
            status integer,
            uri TEXT COLLATE pg_catalog."default" NOT NULL,
            parent_id integer DEFAULT 0,
            width numeric NOT NULL,
            height numeric NOT NULL,
            coordinates numeric[],
            last_update_by TEXT COLLATE pg_catalog."default",
            owner TEXT COLLATE pg_catalog."default",
            migration_key character varying(30) COLLATE pg_catalog."default",
            notes TEXT COLLATE pg_catalog."default",
            labels TEXT[] COLLATE pg_catalog."default",
            source TEXT COLLATE pg_catalog."default" NOT NULL,
            page numeric pg_catalog."default" NULL,
            CONSTRAINT figures_pkey PRIMARY KEY (id),
            CONSTRAINT fk_document_id FOREIGN KEY (doc_id)
                REFERENCES dev.documents (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION
        )

        TABLESPACE pg_default;

        ALTER TABLE IF EXISTS {schema}.figures
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
