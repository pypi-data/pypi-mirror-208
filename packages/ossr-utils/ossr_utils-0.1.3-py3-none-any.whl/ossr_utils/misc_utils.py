import sys
import time
from typing import Optional, List, Union
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_seg_amp_metric(wf):
    """Calculate audio segment amplitude metric"""
    return int(np.max(np.abs(wf)))


def get_ts_now():
    """Get current time in UTC milliseconds"""
    return int(1e3 * time.time())

def print_df_full(df: pd.DataFrame,
                  row_lims: Optional[List[int]] = None):
    """Print all rows and columns of a dataframe"""
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.expand_frame_repr', False):
        if row_lims is None:
            print(df)
        else:
            print(df[row_lims[0]:row_lims[1]])

def convert_utc_to_dt(ts: Union[List[int], int, float]):
    """Convert list of UTC seconds to datetimes in local timezone"""
    if type(ts) is list:
        return [datetime.fromtimestamp(ts_) for ts_ in ts]
    elif (type(ts) is int) or (type(ts) is float):
        return datetime.fromtimestamp(ts)
    else:
        raise TypeError('Specify one of the accepted types for argument "ts".')

def get_colors(n, cmap='jet', mult=1.0):
    return plt.get_cmap(cmap)(np.linspace(0, 1, n))[:, :3] * mult


def get_dists(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    M = x.shape[0]
    N = y.shape[0]
    dists = np.zeros((M, N), dtype='float')
    for j in range(N):
        dists[:, j] = np.sqrt(np.sum((x - y[j, :]) ** 2, axis=1))
    return dists

def get_dists_mahal(X: np.ndarray,
                    mus: np.ndarray,
                    covs: Optional[np.ndarray] = None,
                    covs_inv: Optional[np.ndarray] = None) \
        -> np.ndarray:
    assert (covs is None) ^ (covs_inv is None) # XOR

    N = X.shape[0]
    K = mus.shape[0]
    if covs is not None:
        cmats = covs
    else:
        cmats = covs_inv

    dists = np.zeros((N, K), dtype='float')
    for k in range(K):
        xm = X - mus[k, :]
        if cmats.ndim == 3:
            cmat_k = cmats[:, :, k]
        elif cmats.ndim == 2:
            cmat_k = cmats
        if covs is not None:
            dists[:, k] = np.sum(xm * np.linalg.solve(cmat_k, xm.T).T, axis=1) # (x - mu)^T * S^-1 * (x - mu)
        else:
            dists[:, k] = np.sum(xm * (cmat_k @ xm.T).T, axis=1)

    return dists

def logsumexp(arr: np.ndarray,
              axis: int) \
        -> np.ndarray:
    m = np.max(arr, axis=axis, keepdims=True)
    return m + np.log(np.sum(np.exp(arr - m), axis=axis, keepdims=True))



def tags_str_to_int(tags: List[str],
                    num_tags: int,
                    wild_tag: str = '',
                    tags_all: Optional[List[str]] = None) \
        -> np.ndarray:
    N = len(tags)
    tags_arr = np.ones(N, dtype='int') * num_tags
    for i in range(N):
        if tags_all is None:
            if tags[i] != wild_tag:
                tags_arr[i] = int(tags[i])
        else:
            if tags[i] in tags_all:
                tags_arr[i] = [j for j, tag in enumerate(tags_all) if tags[i] == tag][0]
    return tags_arr

def get_majority_str(strs: List[str]) -> str:
    """Find string that appears most often in list"""
    strs_unique = np.unique(strs)
    counts = [np.sum([s == str_ for s in strs]) for str_ in strs_unique]
    return strs_unique[np.argmax(counts)] # break ties via alphabetical order

def arr_to_lists(arr) -> list:
    """Prepare numpy array for jsonification"""
    lst = []
    for item in arr:
        if isinstance(item, np.ndarray):
            lst.append(arr_to_lists(item))
        else:
            if isinstance(item, np.int64):
                item = int(item)
            lst.append(item)
    return lst


def print_flush(s):
    print(s)
    sys.stdout.flush()


def gauss_pdf(mu: float,
              var: float,
              x: np.ndarray,
              include_norm: bool = True,
              wrap: Optional[List[float]] = None) \
        -> np.ndarray:
    if include_norm:
        c = 1 / np.sqrt(2 * np.pi * var)
    else:
        c = 1
    if not wrap:
        return c * np.exp(-(x - mu) ** 2 / (2 * var))
    else:
        mus = mu + np.arange(-2, 3) * (wrap[1] - wrap[0])
        return c * np.sum(np.exp(-(x[:, np.newaxis] - mus) ** 2 / (2 * var)), axis=1)


def get_times_from_dts(ts: Union[datetime.timestamp, List[datetime.timestamp]]) -> Union[float, np.ndarray]:
    # convert timestamps to time-of-day in hours
    if not isinstance(ts, (list, np.ndarray)):
        ts = [ts]
        islist = False
    else:
        islist = True
    times = [] # hours
    for t_ in ts:
        tm = t_.time()
        times.append(tm.hour + tm.minute / 60 + tm.second / 3600)
    if islist:
        return np.array(times)
    else:
        return times[0]
