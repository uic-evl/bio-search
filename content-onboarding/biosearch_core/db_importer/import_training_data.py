from os import listdir
from sys import argv
import logging
from argparse import ArgumentParser, Namespace
from typing import List
from pathlib import Path
from psycopg import Cursor, connect
import pandas as pd

from biosearch_core.db.model import ConnectionParams, params_from_env
from biosearch_core.data.figure import DBFigure, SubFigureStatus, FigureType


def setup_logger(workspace: str):
    """configure logger"""
    logger_dir = Path(workspace)

    logging.basicConfig(
        filename=str(logger_dir / "import_training.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def insert_figures_to_db(cursor: Cursor, schema: str, figures: List[DBFigure]):
    """Massive import of figures to database"""
    # pylint: disable=line-too-long
    sql = f"COPY {schema}.figures (name,caption,num_panes,fig_type,doc_id,status,uri,parent_id,width,height,coordinates,last_update_by,owner,migration_key,notes,label,source,page,ground_truth) FROM STDIN"
    with cursor.copy(sql) as copy:
        for elem in figures:
            copy.write_row(elem.to_tuple())


def df_to_figures(dataframe: pd.DataFrame) -> List[DBFigure]:
    """Match parquet files to entries for figures table. The split set value
    does not goes in this table because it depends on the classifier"""
    subfigures = []
    for _, row in dataframe.iterrows():
        subfigure = DBFigure(
            caption=row.caption,
            coordinates=None,
            doc_id=None,
            height=row.height,
            name=row.img,
            num_panes=1,
            page=-1,
            parent_id=None,
            source=row.source,
            status=SubFigureStatus.GROUND_TRUTH.value,
            type=FigureType.SUBFIGURE.value,
            uri=row.img_path,
            width=row.width,
        )
        subfigure.ground_truth = row.label
        subfigure.notes = row.original
        subfigures.append(subfigure)
    return subfigures


def insert_figures(conn_params: ConnectionParams, input_folder: str):
    """Insert ground truth from dataframe to db"""
    df_all = pd.read_parquet(Path(input_folder) / "all.parquet")
    subfigures = df_to_figures(df_all)
    # pylint: disable=not-context-manager
    with connect(conninfo=conn_params.conninfo(), autocommit=False) as conn:
        with conn.cursor() as cursor:
            try:
                insert_figures_to_db(cursor, conn_params.schema, subfigures)
            # pylint: disable=broad-except
            except Exception as exc:
                print("Error inserting ground truth", exc)
                logging.error("Error inserting content", exc_info=True)
                conn.rollback()

    # parquet_names = [el for el in listdir(input_folder) if el.endswith(".parquet")]


def parse_args(args) -> Namespace:
    """Parse args from command line"""
    parser = ArgumentParser(prog="import labeled data to db")
    parser.add_argument("dir", type=str, help="folder with parquet files")
    parser.add_argument("db", type=str, help="path to .env with db conn")
    parsed_args = parser.parse_args(args)

    return parsed_args


def main():
    """entry point"""
    args = parse_args(argv[1:])
    setup_logger(str(Path(args.dir)))
    conn_params = params_from_env(args.db)
    insert_figures(conn_params, args.dir)


if __name__ == "__main__":
    main()
