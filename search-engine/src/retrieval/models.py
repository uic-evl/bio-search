from dataclasses import dataclass
from datetime import datetime


@dataclass
class LuceneDocument:
    """
    datetime: str in format "%Y-%m%d" or year alone
    modalities: str with modalities separated by a white space
    """

    docId: int
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
