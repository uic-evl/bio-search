""" Document definitions"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class DocumentType(Enum):
    """Figure type in the database"""

    IMPORTED = "imported"


@dataclass
class DbDocument:
    """Document in database"""

    title: str
    project: str
    status: str
    import_date: datetime
    abstract: Optional[str] = field(default=None)
    authors: Optional[list[str]] = field(default=None)
    publication_date: Optional[datetime] = field(default=None)
    modalities: Optional[list[str]] = field(default=None)
    pmcid: Optional[str] = field(default=None)
    pubmed_id: Optional[int] = field(default=None)
    journal: Optional[str] = field(default=None)
    repository: Optional[str] = field(default=None)
    cord_uid: Optional[str] = field(default=None)
    license: Optional[str] = field(default=None)
    uri: Optional[str] = field(default=None)
    doi: Optional[str] = field(default=None)
    notes: Optional[str] = field(default=None)

    def to_tuple(self):
        """Return data as tuple to insert in database"""
        return (
            self.title if self.title is not None else None,
            self.authors,
            self.abstract if self.abstract is not None else None,
            self.publication_date,
            self.pmcid,
            self.pubmed_id,
            self.journal if self.journal is not None else None,
            self.repository,
            self.project,
            self.license,
            self.status,
            self.uri,
            self.doi,
            self.notes,
            self.import_date,
        )
