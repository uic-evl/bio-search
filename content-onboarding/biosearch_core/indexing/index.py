""" Index parquet file to create Lucene indexes
  Indexing full-text:
    For CORD19 files, provide the metadata.csv file to fetch the location of the 
    full text. If your data has to be retrieved from another source, implement a
    reader like CordReader and pass the data location as a param.

  python index.py --input_path XXXX.parquet --output_path YYYY
"""

import lucene
print("loading java")
lucene.initVM(vmargs=["-Djava.awt.headless=true"])

from sys import argv
from argparse import ArgumentParser, Namespace
import time
from pandas import read_parquet
from rich.console import Console
from biosearch_core.indexing.index_writer import Indexer
from biosearch_core.indexing.CordReader import CordReader

console = Console()

def parse_args(args) -> Namespace:
    """Parse args from command line"""
    parser = ArgumentParser(prog="export indexes to parquet")
    parser.add_argument("input_path", type=str, help="path to parquet file to index")
    parser.add_argument("output_path", type=str, help="path to index storage")
    parser.add_argument('-c', '--cord19_base_path', type=str, default="")
    parsed_args = parser.parse_args(args)

    return parsed_args


def main():
    """Parse args and index"""    
    args = parse_args(argv[1:])

    with console.status("[bold green] indexing data..."):
        fulltext_provider = None
        if args.cord19_base_path != "":
            console.log("Found text provider")
            fulltext_provider = CordReader(args.cord19_base_path)

        console.log("Reading parquet")
        dataframe = read_parquet(args.input_path)
        dataframe.reset_index()
        console.log(f"Indexing {dataframe.shape[0]} documents")

        start_time = time.time()
        indexer = Indexer(args.output_path, create_mode=True)
        indexer.index_from_dataframe(dataframe, fulltext_provider, split_term=";")
        end_time = time.time()
        console.log(f"Finished after {end_time - start_time}")


if __name__ == "__main__":
    main()
