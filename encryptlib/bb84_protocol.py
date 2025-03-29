'''
/********************/
/* bb84_protocol.py */
/*   Version 2.0    */
/*    2025/03/30    */
/********************/
'''
from types import SimpleNamespace
from .encryption_base import EncryptionBase
from .qubit_utils import measureQubit, eigenstates, ket0, ket1
import numpy as np


class BB84Qubit:
    def __init__(self, bit: int, angle_deg: float):
        # classical bit: 0 or 1
        self._mBit = bit

        # basis angle: 0° (diagonal), 90° (rectilinear)
        self._mAngle = angle_deg

        # initial quantum state (ket), fully determined by bit and basis
        self._mState = self._prepareQubit(bit, angle_deg)

    @property
    def mBit(self):
        # access classical bit value
        return self._mBit

    @property
    def mBasis(self):
        # access basis angle used for preparation
        return self._mAngle

    @property
    def mKet(self):
        # access full quantum state (as linear combination of |0⟩ and |1⟩)
        return self._mState

    def _prepareQubit(self, bit, theta_deg):
        # extract eigenstates of the observable at given angle
        v0, v1 = eigenstates(theta_deg)
        # amplitudes on computational basis |0⟩ and |1⟩
        amp0 = v0[0, 0] if bit == 0 else v1[0, 0]
        amp1 = v0[1, 0] if bit == 0 else v1[1, 0]
        # construct the qubit state from amplitudes and basis vectors
        return amp0 * ket0() + amp1 * ket1()

    def Measure(self, theta_deg):
        # perform measurement in specified basis and collapse state
        result, collapsed = measureQubit(self._mState, theta_deg)
        # update internal state to collapsed post-measurement state
        self._mState = collapsed
        # return classical 0 or 1 outcome
        return result


class BB84Protocol(EncryptionBase):
    def __init__(self, s: SimpleNamespace):
        super().__init__()
        self._cfg = s
        self._protocol = 'BB84 Protocol'
        self._qubits_a = []
        self._qubits_e = []
        self._qubits_b = []

    def generateKey(self, seed: int = None):
        # Generate random bits and bases, prepare qubit states
        if seed is not None:
            np.random.seed(seed)
        L = self._cfg.KEY_LENGTH
        bits = np.random.randint(0, 2, L)
        angles = np.random.choice(self._cfg.BASIS, L)
        self._bits_a = bits
        self._angles_a = angles
        self._qubits_a = [BB84Qubit(b, theta) for b, theta
                          in zip(bits, angles)]

    def sendKey(self, eavesdropping=False, seed: int = None):
        # Transmit the key; simulate Eve if enabled
        if seed is not None:
            np.random.seed(seed)
        self._qubits_b.clear()
        self._qubits_e.clear()
        if eavesdropping:
            self._angles_e = np.random.choice(self._cfg.BASIS,
                                              len(self._qubits_a))
            for q, theta_e in zip(self._qubits_a, self._angles_e):
                # Eve measures
                bit, _ = measureQubit(q._mState, theta_e)
                # Eve reconstructs fake qubit
                self._qubits_e.append(BB84Qubit(bit, theta_e))
                # Bob gets Eve's fake qubit
                self._qubits_b.append(BB84Qubit(bit, theta_e))
        else:
            for bit, theta in zip(self._bits_a, self._angles_a):
                # Bob receives true copy
                self._qubits_b.append(BB84Qubit(bit, theta))

    def reconcileKey(self):
        # return if called multiple times as the state of qbit is collapsed
        if self._key is not None:
            return not self._isKeyCompromised
        # Keys based on basis agreement and run QBER check
        length = len(self._qubits_b)
        # Bob chooses random bases
        self._angles_b = np.random.choice(self._cfg.BASIS, length)
        # Bob's outcomes
        bits_b = [q.Measure(theta) for q, theta
                  in zip(self._qubits_b, self._angles_b)]

        bits_a = self._bits_a
        angles_a = self._angles_a

        # Keep positions where Alice and Bob used same basis
        matches = [i for i in range(length)
                   if angles_a[i] == self._angles_b[i]]
        bits_a_matched = [bits_a[i] for i in matches]
        bits_b_matched = [bits_b[i] for i in matches]

        subset_size = min(len(matches), self._cfg.RECONCILIATION_SUBSET)
        if subset_size == 0:
            self._key = None
            self._isKeyValid = False
            self._isKeyCompromised = True
            return

        # Choose a random subset for error estimation (QBER)
        subset_idx = np.random.choice(len(bits_a_matched), subset_size,
                                      replace=False)
        a_subset = [bits_a_matched[i] for i in subset_idx]
        b_subset = [bits_b_matched[i] for i in subset_idx]
        qber = sum(a != b for a, b in zip(a_subset, b_subset)) / subset_size

        if qber < self._cfg.QBER:
            # Remove subset bits, use the rest as the shared key
            data_bits = [bits_a_matched[i] for i in
                         range(len(bits_a_matched)) if i not in subset_idx]
            key_array = np.array(data_bits, dtype=np.uint8)
            self._key = np.packbits(key_array).tobytes()
            self._isKeyValid = True
            self._isKeyCompromised = False
        else:
            self._key = None
            self._isKeyValid = False
            self._isKeyCompromised = True
            return not self._isKeyCompromised


if __name__ == '__main__':
    pass
