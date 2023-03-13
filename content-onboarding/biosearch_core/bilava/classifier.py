""" Definitions for classifier information used by functions"""
from dataclasses import dataclass


@dataclass
class Classifier:
    """Classifier information"""

    short_name: str
    long_name: str
    model_path: str
