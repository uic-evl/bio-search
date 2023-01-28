""" Module with selects during onboarding """

import logging
from content_onboarding.db.model import connect, ConnectionParams


def build_pmc_to_id_mapper(db_params: ConnectionParams) -> dict[str, str]:
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
