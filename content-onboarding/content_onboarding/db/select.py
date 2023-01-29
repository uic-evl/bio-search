""" Module with selects during onboarding """

import logging
from typing import Dict
from content_onboarding.db.model import connect, ConnectionParams, FigureStatus


def build_pmc_to_id_mapper(db_params: ConnectionParams) -> Dict[str, str]:
    """Get a dictionary [pmcid, doc_id] to match figures to their corresponding
    source documents"""
    try:
        conn = connect(db_params)
        sql = f"select id, pmcid from {db_params.schema}.documents where status == 'IMPORTED' and pmcid != ''"
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return {r[1]: r[0] for r in rows}
    # pylint: disable=broad-except
    except Exception as exception:
        logging.error("Failed retrieving document ids\n", exc_info=True)
        raise Exception(exception) from exception
    finally:
        conn.close()


def build_uri_to_id_mapper(db_params: ConnectionParams) -> Dict[str, int]:
    """
    Query the database for the insert figures and create a dictionary that
    matches the figure path to the database id. We can just this match to
    populate the figure id for the labels table.
    """
    try:
        conn = connect(db_params)
        with conn.cursor() as cur:
            cur.execute(
                f"select id, uri from {db_params.schema}.figures WHERE status == {FigureStatus.STATUS_UNLABELED}"
            )
            rows = cur.fetchall()
            return {r[1]: r[0] for r in rows}
    # pylint: disable=broad-except
    except Exception as exception:
        logging.error("Failed retrieving figure ids\n", exc_info=True)
        raise Exception(exception) from exception
    finally:
        conn.close()
