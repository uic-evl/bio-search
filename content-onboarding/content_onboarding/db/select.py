""" Module with selects during onboarding """


from typing import Dict
from content_onboarding.db.model import FigureStatus


def build_pmc_to_id_mapper(cursor, schema: str) -> Dict[str, str]:
    """Get a dictionary [pmcid, doc_id] to match figures to their corresponding
    source documents"""

    sql = f"select id, pmcid from {schema}.documents where status='IMPORTED' and pmcid != ''"
    cursor.execute(sql)
    rows = cursor.fetchall()
    return {r[1]: r[0] for r in rows}


def build_uri_to_id_mapper(cursor, schema: str) -> Dict[str, int]:
    """
    Query the database for the insert figures and create a dictionary that
    matches the figure path to the database id. We can just this match to
    populate the figure id for the labels table.
    """
    cursor.execute(
        f"select id, uri from {schema}.figures WHERE status = {FigureStatus.IMPORTED.value}"
    )
    rows = cursor.fetchall()
    return {r[1]: r[0] for r in rows}
