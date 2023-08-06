


from typing import Tuple

import numpy as np
import scipy


def write_wav(fpath: str,
              sr: int,
              wf: np.ndarray,
              verbose: bool = False):
    assert wf[0].dtype == 'int16'
    if verbose:
        print('Writing wav ({:0.2f} sec) to {}'.format(len(wf) / sr, fpath))
    scipy.io.wavfile.write(fpath, sr, wf)


def read_wav(fpath: str) -> Tuple[int, np.ndarray]:
    return scipy.io.wavfile.read(fpath)
