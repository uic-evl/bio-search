from sys import argv
from argparse import ArgumentParser, Namespace
from biosearch_core.segmentation.commands.FigsplitCommand import FigsplitDockerCommand


def parse_args(args) -> Namespace:
    """Parse args from command line"""
    parser = ArgumentParser(prog="segment")
    parser.add_argument("folder_dir", type=str, help="folder with .jpg images")
    parsed_args = parser.parse_args(args)

    return parsed_args


def main():
    """main entry"""
    args = parse_args(argv[1:])
    commander = FigsplitDockerCommand("exciting_galois")
    commander.execute(args.folder_dir)


if __name__ == "__main__":
    main()
