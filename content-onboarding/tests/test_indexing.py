""" Test cases for the module responsible for transforming the data from 
the database to a parquet file"""

from biosearch_core.indexing.exporter import IndexManager
from biosearch_core.db.model import ConnectionParams

def test_indexer_identifies_all_nodes_in_modalities():
    """ Leaf modalities must be joined with parents
    For example, mic.ele should output mic.ele and mic to enable filtering at
    multiple levels
    """

    fake_conn = ConnectionParams(None, 1, None, None, None, "schema")
    index_mgr = IndexManager(None, fake_conn)
    modalities = ["mic.flu", "mic.ele.sca", "gra.his", "oth"]
    # pylint: disable=W0212:protected-access
    output = index_mgr._add_modality_parents(modalities)
    assert "mic" in output
    assert "mic.flu" in output
    assert "mic.ele.sca" in output
    assert "gra" in output
    assert "gra.his" in output
    assert "oth" in output

def test_indexer_returns_non_for_missing_modalities():
    """ Base case when there are no modalities """
    fake_conn = ConnectionParams(None, 1, None, None, None, "schema")
    index_mgr = IndexManager(None, fake_conn)
    # pylint: disable=W0212:protected-access
    output = index_mgr._add_modality_parents([])
    assert output is None
    output = index_mgr._add_modality_parents(None)
    assert output is None
