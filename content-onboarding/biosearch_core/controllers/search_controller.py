""" Controller for the search api"""
from typing import Dict
from collections import defaultdict
from psycopg import connect, Cursor
from biosearch_core.db.model import ConnectionParams
from biosearch_core.data.document import DocumentModel as dmod


class SearchController:
    """Process the requests from the search api"""

    def __init__(self, conn_params: ConnectionParams):
        self.conn_params = conn_params

    def _fetch_subfigures_per_page(self, cursor: Cursor, doc_id: int) -> Dict:
        subfigures = dmod.fetch_subfigures(cursor, doc_id, self.conn_params.schema)
        subfigures_by_page = defaultdict(list)
        for subfigure in subfigures:
            subfigures_by_page[subfigure.page_number].append(subfigure)
        return subfigures_by_page

    def fetch_surrogate_data(self, doc_id: int) -> Dict:
        """Information to populate surrogate cards"""

        # pylint: disable=not-context-manager
        doc_id = int(doc_id)
        schema = self.conn_params.schema
        with connect(conninfo=self.conn_params.conninfo()) as conn:
            with conn.cursor() as cursor:
                surrogate_info = dmod.fetch_surrogate_details(cursor, doc_id, schema)
                subfigures_by_page = self._fetch_subfigures_per_page(cursor, doc_id)

                pages = []
                for (
                    page_number
                ) in subfigures_by_page:  # pylint: disable=consider-using-dict-items
                    page = {"figures": [], "page": page_number, "page_url": None}
                    # group subfigures by figure for convenience
                    subfigs_by_fig = defaultdict(list)
                    for subfigure in subfigures_by_page[page_number]:
                        subfigs_by_fig[subfigure.figure_id].append(subfigure)

                    # populate metadata for figures
                    for (
                        figure_id
                    ) in subfigs_by_fig:  # pylint: disable=consider-using-dict-items
                        figure = {
                            "caption": subfigs_by_fig[figure_id][0].caption,
                            "page": subfigs_by_fig[figure_id][0].page_number,
                            "url": subfigs_by_fig[figure_id][0].figure_url,
                            "width": int(subfigs_by_fig[figure_id][0].figure_width),
                            "height": int(subfigs_by_fig[figure_id][0].figure_height),
                        }
                        subfigures = []
                        for subfigure in subfigs_by_fig[figure_id]:
                            subfigures.append(
                                {
                                    "name": subfigure.subfigure_id,
                                    "type": subfigure.prediction,
                                    "bbox": subfigure.coordinates,
                                }
                            )
                        figure["subfigures"] = subfigures
                        page["figures"].append(figure)
                    pages.append(page)
        return {
            "title": surrogate_info.title,
            "number_figures": surrogate_info.num_figures,
            "pages": pages,
            "pmcid": surrogate_info.pmcid,
        }
