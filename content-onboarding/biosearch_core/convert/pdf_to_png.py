""" Batch process for converting input PDFs into images"""

from sys import argv
from argparse import ArgumentParser, Namespace
from os import listdir, system
from pathlib import Path
import multiprocessing


def parse_args(args) -> Namespace:
    """Parse args from command line"""
    parser = ArgumentParser(prog="convert pdf to png")
    parser.add_argument("projects_dir", type=str, help="root folder for projects")
    parser.add_argument("project", type=str, help="project name")
    parser.add_argument("source", type=str, help="location of folders to inspect")
    parser.add_argument("-w", "--num_workers", type=int, default=12)

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


def extract(input_path: str, base_target: str):
    """Call xpdf pdftopng"""
    documents = [x for x in listdir(input_path) if x.endswith(".pdf")]
    doc_path = Path(input_path) / documents[0]
    target_path = str(Path(base_target) / Path(input_path).name)

    return system(f"pdftopng -r 300 {str(doc_path)} {target_path}")


def main():
    """main entry"""
    args = parse_args(argv[1:])

    project_folder = Path(args.projects_dir) / args.project
    base_path = project_folder / args.source
    target_path = project_folder / "cord19-pdf-images"

    input_folders = set([elem for elem in listdir(base_path) if elem.startswith("PMC")])
    existing_folders = set(
        [elem for elem in listdir(target_path) if elem.startswith("PMC")]
    )

    input_folders = list(input_folders.difference(existing_folders))

    batch_size = args.num_workers
    items = [(str(base_path / el), str(target_path)) for el in input_folders]

    for data_batch in batch(items, size=batch_size):
        pool = multiprocessing.Pool()
        with multiprocessing.Pool(args.num_workers) as pool:
            _ = pool.starmap(extract, data_batch)
        pool.terminate()


if __name__ == "__main__":
    main()
