""" Create indexes for CORD19
Script reads a parquet file with the exported records from CORD19 and 
write the Lucene indexes in the specified output path.

arguments:
--parquet: Path to the parquet file
--indexes: Path to the folder that will store the indexes. It's preferred that
           the folder is empty as we are writing in create mode
"""

from argparse import ArgumentParser
import lucene
from pandas import read_parquet
from index_writer import Indexer

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="cordParquet2Indexes",
        description="Read a parquet file and output lucene indexes",
    )
    parser.add_argument("-p", "--parquet", type=str)
    parser.add_argument("-i", "--indexes", type=str)
    args = parser.parse_args()

    vm_env = lucene.getVMEnv() or lucene.initVM(  # pylint: disable=no-member
        vmargs=["-Djava.awt.headless=true"]
    )

    df = read_parquet(args.parquet)
    indexer = Indexer(store_path=args.indexes, create_mode=True)
    indexer.index_from_dataframe(df)
