""" Data models used for indexing content in Apache Lucene"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class LuceneCaption:
    """Figure caption to index in Lucene. The figure_id allows matching with the
    database records"""

    figure_id: int
    text: str


@dataclass
class LuceneDocument:  # pylint: disable=too-many-instance-attributes
    """Document to index in Lucene.
    datetime: str in format "%Y-%m%d" or year alone
    modalities: str with modalities separated by a white space
    """

    doc_id: int
    source: str
    title: str
    abstract: str
    pub_date: str
    journal: str
    authors: str
    pmcid: str
    num_figures: int
    modalities: str
    url: str
    captions: Optional[List[LuceneCaption]]
    otherid: str
