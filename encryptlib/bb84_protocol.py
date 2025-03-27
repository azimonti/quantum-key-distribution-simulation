'''
/********************/
/* bb84_protocol.py */
/*   Version 1.0    */
/*    2025/03/27    */
/********************/
'''
from types import SimpleNamespace
from .encryption_base import EncryptionBase
import numpy as np


class BB84Protocol(EncryptionBase):
    def __init__(self, s: SimpleNamespace):
        super().__init__()
        self._cfg = s
        self._protocol = 'BB84 Protocol'

    def generateKey(self, seed: int = None):
        if seed is not None:
            np.random.seed(seed)

    def reconcileKey(self, key):
        pass
