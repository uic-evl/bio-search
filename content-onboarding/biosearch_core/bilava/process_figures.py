""" Module to process the features, prediction probabilities, and active learning
metrics for bilava's strategy"""

from typing import List
import pandas as pd
import pandas.io.sql as sqlio
from psycopg import Connection


def fetch_from_db(
    conn: Connection, classifier: str, schemas: List[str]
) -> pd.DataFrame:
    """Fetch dataframe the will be updated for classifier
    Args:
    - classifier: str
      Short name for classifier. For instance, exp.gel for experimental gel
    - schemas: List[str]
      All schemas that will provide inputs for training
    """

    # Fetch from tables to get train, val, test
    # bilava should have a table that matches the split set per classifier
    # the training data should be treated differently... because the split_set
    # does not exist yet? or i should keep a separate insert for the first time.

    df_schemas = []
    for schema in schemas:
        # pylint: disable=consider-using-f-string
        query = """
                SELECT id, name, uri, width, height, source, status FROM {schema}.figures 
                WHERE label like '{classifier}%'
                """.format(
            schema=schema, classifier=classifier
        )
        df_schema = sqlio.read_sql_query(query, conn)
        df_schema["schema"] = schema

        df_schemas.append(df_schema)
    return pd.concat(df_schemas)
