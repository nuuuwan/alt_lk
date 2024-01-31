import numpy as np
import scipy.sparse as sp
from utils import Log

from utils_future.File import File
from utils_future.Timer import Timer

log = Log('SparseArrayFile')


class SparseArrayFile(File):
    def write(self, np_arr: np.array):
        sparray = sp.csr_matrix(np_arr)
        sp.save_npz(self.path, sparray)
        log.info(f'Wrote {self}.')

    def read(self) -> np.array:
        timer = Timer()
        log.debug(f'Reading {self.path}...')
        log.debug('(🐌 = slow operation)')
        sparray = sp.load_npz(self.path)
        log.debug(f'🐌 Loaded Sparse Array in {timer.lap():.2f}s.')
        np_arr = sparray.toarray()
        log.debug(f'Loaded Dense Array in {timer.lap():.2f}s.')
        return np_arr
