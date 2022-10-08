from dataclasses import dataclass
from datetime import datetime
from dataclasses import field
from typing import Optional

@dataclass
class Cord19Document:
  title: str
  project: str
  status: str
  abstract: Optional[str]  = field(default=None)
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
    """ Return data as tuple to insert in database """
    return (self.title[:200], 
            [x[:100] for x in self.authors] if self.authors is not None else None,
            self.abstract[:2000], 
            self.publication_date,
            self.pmcid,
            self.pubmed_id,
            self.journal[:100],
            self.repository,
            self.project,
            self.license,
            self.status,
            self.uri,
            self.doi,
            self.notes)
