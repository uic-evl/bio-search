import numpy as np


def load_pubmed_data(gxd: list[dict]):
    gxd_pubmed_ids = [x["pmid"] for x in gxd]

    n_splits = len(gxd_pubmed_ids) // 100
    id_splits = np.array_split(gxd_pubmed_ids, n_splits)
