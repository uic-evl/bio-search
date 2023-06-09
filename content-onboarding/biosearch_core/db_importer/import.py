""" Module to import content to database after the folders passed through
extraction and segmentation"""

from sys import argv
from argparse import ArgumentParser, Namespace
from pathlib import Path
import logging
from biosearch_core.db_importer.importer import ImportManager
from biosearch_core.db_importer.loaders import Cord19Loader, GDXLoader
from biosearch_core.db.model import params_from_env


def setup_logger(workspace: str):
    """configure logger"""
    logger_dir = Path(workspace) / "logs"
    if not logger_dir.exists:
        raise Exception("workspace does not exist")

    logging.basicConfig(
        filename=str(logger_dir / "importdb.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def parse_args(args) -> Namespace:
    """Parse args from command line"""
    parser = ArgumentParser(prog="DB Importer")
    parser.add_argument(
        "projects_dir", type=str, help="root folder where projects are stored"
    )
    parser.add_argument("project", type=str, help="project name")
    parser.add_argument("metadata", type=str, help="path to metadata")
    parser.add_argument("db", type=str, help="path to .env with db conn")
    # TODO: temp parameter for setting what importer to use
    parser.add_argument(
        "--loader", "-l", type=str, help="metadata loader", default="cord19"
    )
    parsed_args = parser.parse_args(args)

    return parsed_args


def main():
    """main entry"""
    args = parse_args(argv[1:])
    setup_logger(str(Path(args.projects_dir) / args.project))

    conn_params = params_from_env(args.db)
    manager = ImportManager(args.projects_dir, args.project, conn_params)

    if args.loader == "cord19":
        loader = Cord19Loader()
    elif args.loader == "gdx":
        loader = GDXLoader()
    else:
        raise ValueError(f"{args.loader} loader not supported")
    manager.import_content(args.metadata, loader)


if __name__ == "__main__":
    main()
