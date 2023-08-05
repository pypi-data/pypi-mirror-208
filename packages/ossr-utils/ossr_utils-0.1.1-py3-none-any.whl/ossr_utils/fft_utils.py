from typing import Optional

import numpy as np


def stft(wf: np.ndarray,
         win_size: int,
         hop_size: int,
         p: int = 0,
         win: Optional[np.ndarray] = None) -> np.ndarray:
    '''
    Short-Time Fourier Transform

    :param wf: Mx0 audio
    :param win_size: window size
    :param hop_size: hop size
    :param p: zero-padding length
    :return: S - DxN stft matrix
    '''
    if win is None:
        win = np.hanning(win_size)

    # prepare
    M = len(wf)
    N = int(np.ceil(1.0*(M - win_size) / hop_size) + 1) # no. windows

    # gather windows
    S = np.zeros((win_size, N),dtype='float')
    for f in range(N-1):
        S[:, f] = wf[f * hop_size: win_size + f * hop_size]
    wf_end = wf[(N - 1) * hop_size:]
    S[:len(wf_end), N - 1] = wf_end

    # apply window function
    S = S * win.reshape(win_size, 1)

    # zero-pad
    S = np.vstack((S, np.zeros((p, S.shape[1]))))

    # do FFTs
    S = np.fft.rfft(S, axis=0)

    return S
