""" Process all folders in directory, mounted at /mnt """

from sys import argv
from os import listdir
from argparse import ArgumentParser, Namespace
from pathlib import Path
import logging
import multiprocessing
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
    parser.add_argument("env", type=str, help="docker or pod")
    parser.add_argument("base_dir", type=str, help="base directory in local env")

    parsed_args = parser.parse_args(args)

    return parsed_args


def batch(iterable, size=256):
    """Create an iterable to process a long list in batches.
    Needed to process the data in batches and guarantee that we are not filling
    the memory with the data from processes that were already finished.
    """
    # https://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks
    len_iterable = len(iterable)
    for ndx in range(0, len_iterable, size):
        yield iterable[ndx : min(ndx + size, len_iterable)]


def split(container_name: str, env: str, base_dir: str, pmcid: str) -> bool:
    """Split function to call in parallel"""
    commander = FigsplitCommand(container_name, container_type=env)
    result = commander.execute(base_dir, pmcid)
    if result:
        with open("processed", "a", encoding="utf-8") as f_out:
            f_out.write(f"{pmcid}\n")
        logging.info(pmcid)
    else:
        with open("failed", "a", encoding="utf-8") as f_out:
            f_out.write(f"{pmcid}\n")
    return result


def main():
    """main entry"""
    args = parse_args(argv[1:])
    if args.env not in ["docker", "pod"]:
        raise Exception("Environment should be 'docker' or 'pod'")

    folders = [elem for elem in listdir(args.base_dir) if elem.startswith("PMC")]
    setup_logger(Path(args.base_dir))

    batch_size = 14
    items = [(args.container, args.env, args.base_dir, el) for el in folders]

    for data_batch in batch(items, size=batch_size):
        pool = multiprocessing.Pool()
        with multiprocessing.Pool(args.num_workers) as pool:
            _ = pool.starmap(split, data_batch)
        pool.terminate()


if __name__ == "__main__":
    main()
