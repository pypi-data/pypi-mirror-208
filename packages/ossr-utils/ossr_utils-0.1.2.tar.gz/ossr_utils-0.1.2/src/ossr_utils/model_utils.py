
from typing import List

import numpy as np


def get_conf_mat(tags_train: List[str],
                 tags_test: List[str],
                 tags_test_true: List[str],
                 tags_test_pred: List[str],
                 normalize: bool = False) \
        -> np.ndarray:
    """Compute confusion matrix from train/test tag lists and true and predicted test tags"""
    N_test = len(tags_test_pred)
    num_tags_train = len(tags_train)
    num_tags_test = len(tags_test)

    conf_mat = np.zeros((num_tags_train, num_tags_test), dtype='int') # train tags x test tags
    for i in range(N_test):
        y_pred = [j for j, tag in enumerate(tags_train) if tag == tags_test_pred[i]][0] # idx of train tag
        y_true = [j for j, tag in enumerate(tags_test) if tag == tags_test_true[i]][0] # idx of test tag
        conf_mat[y_pred, y_true] += 1
    if normalize:
        conf_mat = np.round(conf_mat / np.sum(conf_mat, axis=0, keepdims=True) * 100).astype('int')

    return conf_mat