""" Dimensionality reduction operations on cpu/gpu"""

from typing import Literal, Tuple
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from numpy import vstack, ndarray
from pandas import DataFrame
from umap import UMAP
from torch.cuda import device_count
from cuml.manifold import TSNE as cumlTSNE
from cuml import UMAP as cumlUMAP
from cuml import PCA as cumlPCA


def reduce_pca_cpu(features: ndarray, random_state=42) -> Tuple[ndarray, ndarray]:
    """PCA on CPU"""
    reducer = PCA(n_components=2, random_state=random_state)
    embeddings = reducer.fit_transform(features)
    return embeddings[:, 0], embeddings[:, 1]


def reduce_umap_cpu(features: ndarray, random_state=42) -> Tuple[ndarray, ndarray]:
    """UMAP on CPU"""
    reducer = UMAP(n_neighbors=15, min_dist=0.1, random_state=random_state)
    embeddings = reducer.fit_transform(features)
    return embeddings[:, 0], embeddings[:, 1]


def reduce_tsne_cpu(
    features: ndarray, random_state=42, perplexity=3
) -> Tuple[ndarray, ndarray]:
    """tsne on CPU"""
    embeddings = TSNE(
        n_components=2, perplexity=perplexity, random_state=random_state
    ).fit_transform(features)
    return embeddings[:, 0], embeddings[:, 1]


def reduce_pca_gpu(features: ndarray, random_state=42) -> Tuple[ndarray, ndarray]:
    """PCA on GPU"""
    print("running pca on gpu")
    reducer = cumlPCA(n_components=2, random_state=random_state)
    embeddings = reducer.fit_transform(features)
    return embeddings[:, 0], embeddings[:, 1]


def reduce_umap_gpu(features: ndarray, random_state=42) -> Tuple[ndarray, ndarray]:
    """UMAP on GPU"""
    print("running umap on gpu")
    reducer = cumlUMAP(
        n_neighbors=15,
        n_components=2,
        n_epochs=500,
        min_dist=0.1,
        random_state=random_state,
    )
    embeddings = reducer.fit_transform(features)
    return embeddings[:, 0], embeddings[:, 1]


def reduce_tsne_gpu(
    features: ndarray, random_state=42, perplexity=30
) -> Tuple[ndarray, ndarray]:
    """tsne on GPU"""
    print("running tsne on gpu")
    embeddings = cumlTSNE(
        n_components=2,
        perplexity=perplexity,
        method="barnes_hut",
        random_state=random_state,
    ).fit_transform(features)
    return embeddings[:, 0], embeddings[:, 1]


def reduce_embeddings(
    input_df: DataFrame, method: Literal["pca", "umap", "tsne"], random_state=42
) -> Tuple[ndarray, ndarray]:
    """Calculate embeddings for first and second dimensions"""
    print("devices available: ", device_count())
    features = vstack(input_df.features)
    # check gpu available
    if device_count() > 0:
        if method == "pca":
            return reduce_pca_gpu(features, random_state=random_state)
        if method == "umap":
            return reduce_umap_gpu(features, random_state=random_state)
        if method == "tsne":
            return reduce_tsne_gpu(features, random_state=random_state)
        raise ValueError(f"{method} method not supported")

    # cpu options
    if method == "pca":
        return reduce_pca_cpu(features, random_state=random_state)
    if method == "umap":
        return reduce_umap_cpu(features, random_state=random_state)
    if method == "tsne":
        return reduce_tsne_cpu(features, random_state=random_state)
    raise ValueError(f"{method} method not supported")
