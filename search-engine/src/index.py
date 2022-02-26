""" 
  Main script to batch index a set of documents
  python index.py --input_path XXXX --output_path YYYY
"""

import argparse
import time
import lucene
from pandas import read_parquet
from retrieval.index_writer import Indexer


def main():
    """ Parse args and index """
    parser = argparse.ArgumentParser(description="Get indexing params")
    parser.add_argument('--input_path',
                        type=str,
                        help="path to parquet file to index")
    parser.add_argument('--output_path',
                        type=str,
                        help="path to index storage")
    args = parser.parse_args()

    dataframe = read_parquet(args.input_path)
    dataframe.reset_index()
    print(f"Indexing {dataframe.shape[0]} documents")

    start_time = time.time()
    indexer = Indexer(args.output_path, create_mode=True)
    indexer.index_from_dataframe(dataframe=dataframe, split_term=";")
    end_time = time.time()
    print(f"Finished after {end_time - start_time}")


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    main()
