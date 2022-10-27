from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class Figure:
  status: str
  uri: str
  width: float
  height: float
  type: int
  source: str
  id: Optional[int]
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
    return (self.name,
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
            self.source)


@dataclass
class Observation:
  id: int
  figure_id: int
  needs_cropping: bool
  is_compound: bool
  is_overcropped: bool
  is_missing_subfigures: bool
  is_close_up: bool
  is_missing_subfigures:bool
  is_missing_panels: bool
  is_overfragmented: bool
  num_subpanes: int
  composition: Optional[str]

  def to_tuple(self):
    return (self.needs_cropping,
            self.is_compound,
            self.is_overcropped,
            self.is_missing_subfigures,
            self.is_close_up,
            self.num_subpanes,
            self.is_missing_panels,
            self.figure_id,
            self.is_overfragmented,
            self.composition)

@dataclass
class Label:
  figure_id: int
  classifier: str
  label: Optional[str]
  prediction: Optional[str]
  features: Optional[np.ndarray]
  pred_probs: Optional[np.ndarray]
  margin_sample: Optional[float]
  entropy: Optional[float]
  split_set: str

  def to_tuple(self):
    return (
      self.figure_id,
      self.classifier,
      self.label,
      self.prediction,
      self.features.tolist(),
      self.pred_probs.tolist(),
      self.margin_sample,
      self.entropy,
      self.split_set
    )
  

