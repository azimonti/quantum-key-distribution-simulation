'''
/********************/
/* bb84_protocol.py */
/*   Version 1.0    */
/*    2025/03/29    */
/********************/
'''
from types import SimpleNamespace
from .encryption_base import EncryptionBase
import numpy as np


class BB84Qubit:
    def __init__(self, bit: int, basis: int):
        self._mBit = bit      # 0 or 1
        self._mBasis = basis  # 0: rectilinear (+), 1: diagonal (x)

    @property
    def mBit(self):
        return self._mBit

    @property
    def mBasis(self):
        return self._mBasis

    def Measure(self, measurementBasis: int):
        if measurementBasis == self._mBasis:
            return self._mBit
        else:
            return np.random.randint(0, 2)


class BB84Protocol(EncryptionBase):
    def __init__(self, s: SimpleNamespace):
        super().__init__()
        self._cfg = s
        self._protocol = 'BB84 Protocol'
        self._qubits_a = []
        self._qubits_e = []
        self._qubits_b = []

    def generateKey(self, seed: int = None):
        if seed is not None:
            np.random.seed(seed)
        length = self._cfg.KEY_LENGTH
        bits = np.random.randint(0, 2, length)
        bases = np.random.randint(0, 2, length)
        self._qubits_a = [BB84Qubit(b, ba) for b, ba in zip(bits, bases)]
        return self._qubits_a

    def sendKey(self, eavesdropping=False, seed: int = None):
        if eavesdropping:
            if seed is not None:
                np.random.seed(seed)
            length = len(self._qubits_a)
            bases_e = np.random.randint(0, 2, length)
            self._qubits_e.clear()
            self._qubits_b.clear()
            for q, b_e in zip(self._qubits_a, bases_e):
                m = q.Measure(b_e)
                # Eve resends measured qubit and Bob receives tampered qubit
                self._qubits_e.append(BB84Qubit(m, b_e))
                self._qubits_b.append(BB84Qubit(m, b_e))
        else:
            self._qubits_b = [BB84Qubit(q.mBit, q.mBasis)
                              for q in self._qubits_a]

    def reconcileKey(self):
        length = len(self._qubits_b)
        bases_b = np.random.randint(0, 2, length)
        bits_b = [q.Measure(b) for q, b in zip(self._qubits_b, bases_b)]

        bits_a = [q.mBit for q in self._qubits_a]
        bases_a = [q.mBasis for q in self._qubits_a]

        matches = [i for i in range(length) if bases_a[i] == bases_b[i]]
        bits_a_matched = [bits_a[i] for i in matches]
        bits_b_matched = [bits_b[i] for i in matches]

        subset_size = min(len(matches), self._cfg.RECONCILIATION_SUBSET)
        subset_idx = np.random.choice(len(bits_a_matched), subset_size,
                                      replace=False)
        a_subset = [bits_a_matched[i] for i in subset_idx]
        b_subset = [bits_b_matched[i] for i in subset_idx]

        qber = sum(a != b for a, b in zip(a_subset, b_subset)) / subset_size

        if qber < self._cfg.QBER:
            key_bits = [bits_a_matched[i] for i in range(
                len(bits_a_matched)) if i not in subset_idx]
            key_array = np.array(key_bits, dtype=np.uint8)
            self._key = np.packbits(key_array).tobytes()
            self._isKeyValid = True
            self._isKeyCompromised = False
        else:
            self._key = None
            self._isKeyValid = False
            self._isKeyCompromised = True
        return self._isKeyCompromised


if __name__ == '__main__':
    pass
