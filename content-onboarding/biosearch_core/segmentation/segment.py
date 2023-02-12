""" Segment a single folder """

from sys import argv
from argparse import ArgumentParser, Namespace
from pathlib import Path
import logging
from biosearch_core.segmentation.commands.figsplit_command import FigsplitCommand


def setup_logger(workspace: str):
    """configure logger"""
    logger_dir = Path(workspace)
    if not logger_dir.exists:
        raise Exception("workspace does not exist")

    logging.basicConfig(
        filename=str(logger_dir / "segment.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def parse_args(args) -> Namespace:
    """Parse args from command line"""
    parser = ArgumentParser(prog="segment")
    parser.add_argument("container", type=str, help="container name")
    parser.add_argument("base_dir", type=str, help="base directory in local env")
    parser.add_argument("folder_dir", type=str, help="relative target dir")

    parsed_args = parser.parse_args(args)

    return parsed_args


def main():
    """main entry"""
    args = parse_args(argv[1:])

    setup_logger(Path(args.base_dir) / args.folder_dir)
    commander = FigsplitCommand(args.container)
    _ = commander.execute(args.base_dir, args.folder_dir)


if __name__ == "__main__":
    main()
