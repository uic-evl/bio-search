""" Module to create documents and figure tables """

from sys import argv
from os import getcwd
from argparse import ArgumentParser, Namespace
from pathlib import Path
import logging
from psycopg import connect
from biosearch_core.db.model import params_from_env
from biosearch_core.db_importer.tables import (
    create_documents_table,
    create_figures_table,
)


def setup_logger(workspace: str):
    """configure logger"""
    logging.basicConfig(
        filename=str(Path(workspace) / "createtables.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def parse_args(args) -> Namespace:
    """Parse args from command line"""
    parser = ArgumentParser(prog="create tables")
    parser.add_argument("db", type=str, help="path to .env with db conn")
    parsed_args = parser.parse_args(args)

    return parsed_args


def create_tables(params):
    """Create database tables"""
    # pylint: disable=not-context-manager
    with connect(conninfo=params.conninfo(), autocommit=False) as conn:
        with conn.cursor() as cursor:
            try:
                schema = params.schema
                owner = params.user
                cursor.execute(create_documents_table(schema, owner))
                cursor.execute(create_figures_table(schema, owner))
            # pylint: disable=broad-except
            except Exception as exc:
                print("Erorr creating tables", exc)
                logging.error("Error creating tables", exc_info=True)
                conn.rollback()


def main():
    """main entry"""
    args = parse_args(argv[1:])
    workspace = getcwd()
    setup_logger(workspace)

    conn_params = params_from_env(args.db)
    create_tables(conn_params)


if __name__ == "__main__":
    main()
