""" Entry point for exporting data for indexing.
The module searches for documents, captions and modality information for documents
with a status ready for indexing, and save the data in a parquet file in a given
location. The data can be later use by the search engine to create the parquet 
indexes.
"""

from sys import argv
from argparse import ArgumentParser, Namespace
from pathlib import Path
import logging
from biosearch_core.indexing.exporter import IndexManager
from biosearch_core.db.model import params_from_env


def setup_logger(workspace: str):
    """configure logger"""
    logger_dir = Path(workspace) / "logs"
    if not logger_dir.exists:
        raise Exception("workspace does not exist")

    logging.basicConfig(
        filename=str(logger_dir / "export.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def parse_args(args) -> Namespace:
    """Parse args from command line"""
    parser = ArgumentParser(prog="export indexes to parquet")
    parser.add_argument("projects_dir", type=str, help="root folder for projects")
    parser.add_argument("project", type=str, help="project name")
    parser.add_argument("db", type=str, help="path to .env with db conn")
    parser.add_argument("output_file", type=str, help="path to output parquet")
    parsed_args = parser.parse_args(args)

    return parsed_args


def main():
    """main entry"""
    args = parse_args(argv[1:])
    setup_logger(str(Path(args.projects_dir) / args.project))

    conn_params = params_from_env(args.db)
    manager = IndexManager(args.project, conn_params)
    manager.to_parquet(args.output_file)


if __name__ == "__main__":
    main()
