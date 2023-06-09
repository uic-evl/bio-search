""" Data class for search results, and encoding for REST response """
import json
from typing import List
from dataclasses import dataclass, field

from biosearch_core.indexing.lucene import LuceneCaption


@dataclass
class SearchResult:
    """keep track of results from index"""

    id: str
    title: str
    abstract: str
    publish_date: str
    modalities: List[str]
    num_figures: int
    url: str
    full_text: str
    journal: str
    authors: str
    captions: List[LuceneCaption]
    modalities_count: dict = field(init=False, default_factory=dict)
    otherid: str


class SearchResultEncoder(json.JSONEncoder):
    """Encode search result to json"""

    def default(self, o):
        if isinstance(o, SearchResult):
            return o.__dict__
        if isinstance(o, LuceneCaption):
            return o.__dict__
        # Base class default() raises TypeError:
        return json.JSONEncoder.default(self, o)
