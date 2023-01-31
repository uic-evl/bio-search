""" Every update on database """

from typing import List
from psycopg import sql
from content_onboarding.db.model import SubFigureStatus


def update_predictions_in_figures(cursor, schema: str, values: List):
    """Update subfigures during prediction phase"""
    length = len(values) // 2
    single_query = (
        f"UPDATE {schema}.figures SET status={SubFigureStatus.PREDICTED.value}, "
    )
    single_query += "label=('{}') WHERE id=({}); "

    all_queries = single_query * length
    query = sql.SQL(all_queries.format(*values))
    cursor.execute(query)
