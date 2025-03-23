'''
/********************/
/* no_encryption.py */
/*   Version 1.0    */
/*    2025/03/23    */
/********************/
'''
from types import SimpleNamespace
from .encryption_base import EncryptionBase
import numpy as np


class NoEncryption(EncryptionBase):
    def __init__(self, s: SimpleNamespace):
        super().__init__()
        self._cfg = s
        self._protocol = 'No Protocol'

    def generateKey(self, seed: int = None):
        if seed is not None:
            np.random.seed(seed)
        bits = np.random.randint(0, 2, self._cfg.KEY_LENGTH, dtype=np.uint8)
        self._key = np.packbits(bits).tobytes()
        self._isKeyValid = True

    def reconcileKey(self, key):
        self._isKeyValid = True
