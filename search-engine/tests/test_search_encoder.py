""" Tests for data structures used in Reader """
import json
from src.retrieval.search_results import SearchResult, SearchResultEncoder


def test_encoder():
    """ test the encoder used to return search results in Flask"""
    title = "some title"
    abstract = "some long abstract"
    publication_date = "2020-02-01"
    modalities = ['mod1', 'mod1.mod3']
    results = [
        SearchResult(title=title,
                     abstract=abstract,
                     publish_date=publication_date,
                     modalities=modalities)
    ]
    encoded = json.dumps(results, cls=SearchResultEncoder, indent=2)
    assert title in encoded
    assert abstract in encoded
    assert publication_date in encoded
    assert modalities[0] in encoded
    assert modalities[1] in encoded
