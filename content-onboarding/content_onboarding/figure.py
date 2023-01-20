""" Classes for Figures """
import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict
from pandas import Series
from pathlib import Path


class FigureStatus(Enum):
    """Figure status in database
    NEW: The image was extracted or imported but not segmentation has been done
    IN_PROCESS: Segmentation has been done, but not all subfigures modalities
        have a ground-truth value or prediction
    PREPROCESSED: Every subfigure has a modality value
    """

    NEW = 0
    IN_PROCESS = 1
    PREPROCESSED = 2


class SubFigureStatus(Enum):
    """Subfigure status in database
    Labeled: Contains ground-truth relevant to taxonomy
    Unlabeled: Imported to db but value not yet predicted
    Predicted: Label predicted by model
    Status workflow:
      [X] -----> Unlabeled -----> Predicted -----> Labeled
       |                              ^                ^
       |______________________________|________________|
    """

    LABELED = 0
    UNLABELED = 1
    PREDICTED = 2


class FigureType(Enum):
    """Indicates Figure or Subfigure (extracted content)"""

    TYPE_FIGURE = 0
    TYPE_SUBFIGURE = 1


@dataclass
class Figure:
    """Represent a figure or subfigure in a dataset"""

    status: FigureStatus
    uri: str
    width: float
    height: float
    type: FigureType
    source: str
    db_id: Optional[int]
    name: Optional[str]
    caption: Optional[str]
    num_panes: Optional[int]
    doc_id: Optional[int]
    parent_id: Optional[int]
    coordinates: Optional[list[float]]
    last_update_by: Optional[str]
    owner: Optional[str]
    migration_key: Optional[str]
    notes: Optional[str]
    labels: Optional[list[str]]

    def to_tuple(self):
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
            self.labels,
            self.source,
        )
