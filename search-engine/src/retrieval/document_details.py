from utils import simple_select

# sample id 7598760


def query_document_details(id):
    """simple query to documents table by id"""
    return (
        f"SELECT d.id, d.title, d.authors, d.journal, COUNT(f.id) "
        f"FROM dev.documents d, dev.figures f "
        f"WHERE d.id = {id} and f.doc_id = d.id and f.fig_type=0 "
        f"GROUP BY d.id"
    )


def query_fig_subfigs(id):
    """get the figures and subfigures data for a document"""
    return (
        f"SELECT f.id as figId, sf.id as subfigId, f.caption, f.uri, sf.uri, "
        f"       sf.coordinates, l.prediction "
        f"FROM dev.figures f, dev.figures sf, dev.labels_cord19 l"
        f"WHERE f.doc_id = {id} AND f.fig_type=0 AND and sf.parent_id = f.id "
        f"      AND sf.id = l.figure_id "
        f"      AND and (sf.id, CHAR_LENGTH(l.prediction)) IN "
        f"        ("
        f"          SELECT sf2.id, MAX(CHAR_LENGTH(l2.prediction))"
        f"          FROM dev.figures sf2, dev.labels_cord19 l2 "
        f"          WHERE sf2.doc_id = {id} AND sf2.fig_type = 1 AND sf2.id = l2.figure_id"
        f"          GROUP BY sf2.id"
        f"        )"
        f"ORDER BY f.id asc      "
    )


def fetch_doc_by_id(db_params, id):
    """Document details to return when surrogate is opened"""
    query = query_document_details(id)
    rows = simple_select(db_params, query)
    if rows:
        document = rows[0]
    else:
        raise Exception(f"data not found for document {id}")
