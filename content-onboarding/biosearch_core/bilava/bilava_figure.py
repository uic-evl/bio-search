""" For table features in schema bilava"""

from dataclasses import dataclass
from typing import List


@dataclass
class BilavaFigure:
    """Class that holds bilava's attributes"""

    id: int  # PK
    schema: str  # PK
    classifier: str  # PK
    label: str
    prediction: str
    name: str
    uri: str
    width: int
    height: int
    source: str
    status: int
    split_set: str
    x_pca: float
    y_pca: float
    x_tsne: float
    y_tsne: float
    x_umap: float
    y_umap: float
    pred_probs: List[float]
    margin_sample: float
    entropy: float
    hit_pca: float
    hit_tsne: float
    hit_umap: float

    def to_tuple(self):
        """for db"""
        return (
            self.id,
            self.schema,
            self.classifier,
            self.label,
            self.prediction,
            self.name,
            self.uri,
            self.width,
            self.height,
            self.source,
            self.split_set,
            self.x_pca,
            self.y_pca,
            self.x_tsne,
            self.y_tsne,
            self.x_umap,
            self.y_umap,
            self.pred_probs,
            self.margin_sample,
            self.entropy,
            self.hit_pca,
            self.hit_tsne,
            self.hit_umap,
            self.status,
        )
