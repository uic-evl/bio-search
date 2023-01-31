from .utils import simple_select
from dataclasses import dataclass, field

# sample id 7598760


def query_document_details(id, schema):
    """simple query to documents table by id"""
    return (
        f"SELECT d.id, d.title, d.authors, d.journal, COUNT(f.id), d.pmcid "
        f"FROM {schema}.documents d, {schema}.figures f "
        f"WHERE d.id = {id} and f.doc_id = d.id and f.fig_type=0 "
        f"GROUP BY d.id"
    )


def query_fig_subfigs(doc_id: int, schema: str):
    """get the figures and subfigures data for a document"""
    return """
        SELECT f.id as figId, sf.id as subfigId, f.caption, f.uri, sf.uri, sf.coordinates, sf.label as prediction, f.width, f.height, f.page
        FROM {schema}.figures f, {schema}.figures sf, {schema}.documents d
        WHERE d.id={doc_id} and d.id = f.doc_id and f.fig_type=0  and f.id = sf.parent_id 
    """.format(
        schema=schema, doc_id=doc_id
    )


# def query_fig_subfigs(id, schema):
#     """get the figures and subfigures data for a document"""
#     return (
#         f"SELECT f.id as figId, sf.id as subfigId, f.caption, f.uri, sf.uri,"
#         f"       sf.coordinates, l.prediction, f.width, f.height "
#         f"FROM {schema}.figures f, {schema}.figures sf, {schema}.labels_cord19 l "
#         f"WHERE f.doc_id = {id} AND f.fig_type=0 AND sf.parent_id = f.id "
#         f"      AND sf.id = l.figure_id "
#         f"      AND (sf.id, CHAR_LENGTH(l.prediction)) IN "
#         f"        ("
#         f"          SELECT sf2.id, MAX(CHAR_LENGTH(l2.prediction))"
#         f"          FROM {schema}.figures sf2, {schema}.labels_cord19 l2 "
#         f"          WHERE sf2.doc_id = {id} AND sf2.fig_type = 1 AND sf2.id = l2.figure_id"
#         f"          GROUP BY sf2.id"
#         f"        )"
#         f"ORDER BY f.id asc      "
#     )


@dataclass
class Subfigure:
    """Convenient structure for rows from query query_fig_subfigs"""

    figure_id: int
    subfigure_id: int
    caption: str
    figure_url: str
    subfigure_url: str
    coordinates: list[float]
    prediction: str
    figure_width: float
    figure_height: float
    page_number: int

    def __post_init__(self):
        if self.coordinates:
            self.coordinates = [float(x) for x in self.coordinates]


@dataclass
class QueriedDocument:
    """Document information queried"""

    doc_id: int
    title: str
    authors: str
    number_figures: int
    pmcid: str


def fetch_subfigures(db_params: dict, schema: str, id: int) -> list[Subfigure]:
    """Fetch subfigures information for document"""
    records = simple_select(db_params, query_fig_subfigs(id, schema))
    subfigures = []
    for record in records:
        subfigures.append(
            Subfigure(
                figure_id=record[0],
                subfigure_id=record[1],
                caption=record[2],
                figure_url=record[3],
                subfigure_url=record[4],
                coordinates=record[5],
                prediction=record[6],
                figure_width=record[7],
                figure_height=record[8],
                page_number=record[9],
            )
        )
    return subfigures


def fetch_doc_by_id(db_params, schema, id):
    """Document details to return when surrogate is opened"""
    rows = simple_select(db_params, query_document_details(id, schema))
    if rows:
        document = QueriedDocument(
            doc_id=rows[0][0],
            title=rows[0][1],
            authors=rows[0][2],
            number_figures=rows[0][4],
            pmcid=rows[0][5],
        )
    else:
        raise Exception(f"data not found for document {id}")
    subfigures = fetch_subfigures(db_params, schema, id)

    subfigures_by_page = {}
    for subfigure in subfigures:
        if subfigure.page_number in subfigures_by_page:
            subfigures_by_page[subfigure.page_number].append(subfigure)
        else:
            subfigures_by_page[subfigure.page_number] = [subfigure]

    pages = []
    for page_number in subfigures_by_page:  # pylint: disable=consider-using-dict-items
        page = {"figures": [], "page": page_number, "page_url": None}
        subfigs_by_fig = {}
        # group subfigures by figure for convenience
        for subfigure in subfigures_by_page[page_number]:
            if subfigure.figure_id in subfigs_by_fig:
                subfigs_by_fig[subfigure.figure_id].append(subfigure)
            else:
                subfigs_by_fig[subfigure.figure_id] = [subfigure]
        # populate metadata for figures
        for figure_id in subfigs_by_fig:  # pylint: disable=consider-using-dict-items
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
        "title": document.title,
        "number_figures": document.number_figures,
        "pages": pages,
        "pmcid": document.pmcid,
    }
