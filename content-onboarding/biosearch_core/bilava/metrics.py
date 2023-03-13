""" Metrics for active learning"""

import numpy as np


def calc_margin_sampling(y_pred_prob):
    """Margin sampling"""
    return np.diff(-np.sort(y_pred_prob)[:, ::-1][:, :2])


def calc_entropy(y_pred_prob):
    """Entropy"""
    return -np.nansum(np.multiply(y_pred_prob, np.log(y_pred_prob)), axis=1)
