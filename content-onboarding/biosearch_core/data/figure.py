""" Definitions for figures"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class FigureType(Enum):
    """Figure type in the database"""

    FIGURE = 0
    SUBFIGURE = 1


class FigureStatus(Enum):
    """Figure status in the database
    Imported: The figure was imported from after segmentation
    Verified: Every subfigure has been validated
    """

    IMPORTED = 0
    VERIFIED = 1


class SubFigureStatus(Enum):
    """Subfigure status in database
    Not predicted: The record was just imported from disk
    Predicted: A model estimated the label
    Ground Truth: Someone validated the label
    """

    NOT_PREDICTED = 2
    PREDICTED = 3
    GROUND_TRUTH = 4


@dataclass
class DBFigure:
    """Figure in database"""

    status: str
    uri: str
    width: float
    height: float
    type: int
    source: str
    name: Optional[str]
    caption: Optional[str]
    num_panes: Optional[int]
    doc_id: Optional[int]
    parent_id: Optional[int]
    coordinates: Optional[list[float]]
    last_update_by: str = field(init=False, default=None)
    db_id: int = field(init=False, default=None)
    owner: str = field(init=False, default=None)
    migration_key: str = field(init=False, default=None)
    notes: str = field(init=False, default=None)
    label: str = field(init=False, default=None)
    page: Optional[int]

    def to_tuple(self):
        """Return data as tuple to insert in database"""
        return (
            self.name,
            self.caption,
            self.num_panes,
            self.type,
            self.doc_id,
            self.status,
            self.uri,
            self.parent_id,
            self.width,
            self.height,
            self.coordinates,
            self.last_update_by,
            self.owner,
            self.migration_key,
            self.notes,
            self.label,
            self.source,
            self.page,
        )
