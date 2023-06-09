""" Module for the labeling session 
Table: session
"""
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
from pandas import DataFrame


@dataclass
class LabelingSession:
    """Represent a summary of the labeling updates in BI-LAVA before iterating"""

    # pylint: disable=C0103:invalid-name
    id: int = field(init=False)
    end_date: datetime
    number: int
    num_updates: int
    num_errors: int
    num_classifiers: int

    def to_tuple(self):
        """to insert to db"""
        return (
            self.end_date,
            self.number,
            self.num_updates,
            self.num_errors,
            self.num_classifiers,
        )


def create_session(
    end_date: datetime,
    subfigures: List[Dict],
    classifiers: List[str],
    session_number: int,
) -> LabelingSession:
    df_subfigures = DataFrame.from_dict(subfigures)
    df_subfigures["error"] = df_subfigures.apply(
        lambda x: 1 if "error" in x["upt_label"] else 0, axis=1
    )
    num_errors = df_subfigures.error.sum()
    num_updates = df_subfigures.shape[0] - num_errors
    num_classifiers = len(classifiers)

    return LabelingSession(
        end_date=end_date,
        number=session_number,
        num_updates=num_updates,
        num_errors=num_errors,
        num_classifiers=num_classifiers,
    )
