""" Definitions for figures"""
from enum import Enum


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
