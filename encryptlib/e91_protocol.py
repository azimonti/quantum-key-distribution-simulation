'''
/*******************/
/* e91_protocol.py */
/*  Version 1.0    */
/*   2025/04/05    */
/*******************/
'''
from types import SimpleNamespace
from .encryption_base import EncryptionBase
from .qubit_utils import ket0, ket1, tensor, observable, measureQubit, \
    normalize
import numpy as np


class E91QubitPair:
    # Represents a maximally entangled Bell state: (|00⟩ + |11⟩)/√2
    def __init__(self):
        psi = (1 / np.sqrt(2)) * (tensor(ket0(), ket0())
                                  + tensor(ket1(), ket1()))
        # 4x1 column vector
        self.mState = psi.reshape((4, 1))


def localMeasure(state, theta_deg, which: str):
    # Perform a local measurement on a specified side
    # (A or B) of the entangled system
    obs = observable(theta_deg)
    _, eigvecs = np.linalg.eigh(obs)
    # orthonormal measurement basis
    basis = [eigvecs[:, 0:1], eigvecs[:, 1:2]]

    # joint entangled two-qubit state
    if state.shape == (4, 1):
        psi = state.reshape(4, 1)
        psi2 = psi.reshape(2, 2)

        if which == 'A':
            probs = [np.linalg.norm(b.conj().T @ psi2[:, :])**2
                     for b in basis]
        elif which == 'B':
            probs = [np.linalg.norm(b.conj().T @ psi2.T[:, :])**2
                     for b in basis]
        else:
            raise ValueError("which must be 'A' or 'B'")

        probs = [max(0.0, np.real(p)) for p in probs]
        total = sum(probs)
        probs = [p / total if total > 0 else 0.5 for p in probs]

        result = np.random.choice([0, 1], p=probs)
        vec = basis[result]
        # projection operator
        proj_op = vec @ vec.conj().T

        if which == 'A':
            # project Alice's side
            proj = tensor(proj_op, np.eye(2))
        else:
            # project Bob's side
            proj = tensor(np.eye(2), proj_op)

        collapsed = proj @ psi
        collapsed = normalize(collapsed)
        psi2 = collapsed.reshape(2, 2)

        if which == 'A':
            reduced = psi2[result, :].reshape(2, 1)
        else:
            reduced = psi2[:, result].reshape(2, 1)

        reduced = normalize(reduced)
        return result, reduced

    # Bob's product state qubit post-Eve
    elif state.shape == (2, 1):
        result, _ = measureQubit(state, theta_deg)
        return result, None

    else:
        raise ValueError(f"Invalid state shape: {state.shape}")


class E91Protocol(EncryptionBase):
    def __init__(self, s: SimpleNamespace):
        super().__init__()
        self._cfg = s
        self._protocol = "Ekert Protocol"
        self._anglesA = []
        self._anglesB = []
        self._anglesE = []
        self._resultsA = []
        self._resultsB = []
        self._resultsE = []
        self._pairs = []

    def generateKey(self, seed: int = None):
        # Prepare entangled pairs and randomly chosen measurement angles
        if seed is not None:
            np.random.seed(seed)
        L = self._cfg.KEY_LENGTH
        self._anglesA = np.random.choice(self._cfg.BASIS_A, L)
        self._anglesB = np.random.choice(self._cfg.BASIS_B, L)
        self._pairs = [E91QubitPair() for _ in range(L)]

    def sendKey(self, eavesdropping=False, seed: int = None):
        # Simulate transmission and measurement; insert Eve if enabled
        if seed is not None:
            np.random.seed(seed)
        self._resultsA.clear()
        self._resultsB.clear()
        self._resultsE.clear()
        self._anglesE.clear()

        for i, pair in enumerate(self._pairs):
            thetaA = self._anglesA[i]
            thetaB = self._anglesB[i]
            state = pair.mState

            if eavesdropping:
                thetaE = np.random.choice(self._cfg.BASIS_E)
                self._anglesE.append(thetaE)

                # Alice measures her half (entanglement collapses)
                a_result, b_state = localMeasure(state, thetaA, 'A')
                # Eve intercepts Bob's qubit and measures it
                e_result, _ = localMeasure(b_state, thetaE, 'B')
                # Bob receives recreated qubit (same bit Eve saw)
                self._resultsA.append(a_result)
                self._resultsE.append(e_result)
                self._resultsB.append(e_result)
            else:
                # No Eve: Alice gets collapse result
                # and Bob gets the corresponding reduced state
                a_result, b_state = localMeasure(state, thetaA, 'A')
                b_result, _ = localMeasure(tensor(ket0(), b_state),
                                           thetaB, 'B')
                self._resultsA.append(a_result)
                self._resultsB.append(b_result)

    def _expectation(self, a_deg, b_deg):
        vals = []
        for angleA, angleB, rA, rB in zip(self._anglesA, self._anglesB,
                                          self._resultsA, self._resultsB):
            if angleA == a_deg and angleB == b_deg:
                A = 1 if rA == 0 else -1
                B = 1 if rB == 0 else -1
                vals.append(A * B)
        return np.mean(vals) if vals else 0.0

    def reconcileKey(self):
        # return early if already processed
        if self._key is not None:
            return not self._isKeyCompromised

        # extract key bits: only events with (0°, 0°) on Alice and Bob
        key_indices = [i for i in range(len(self._anglesA))
                       if self._anglesA[i] == 0 and self._anglesB[i] == 0]
        bitsA_key = np.array([self._resultsA[i] for i in key_indices])

        # fail if no key bits available at all
        if len(bitsA_key) == 0:
            self._key = None
            self._isKeyValid = False
            self._isKeyCompromised = True
            return

        # compute CHSH violation score from configured angle pairs
        a0, a1 = self._cfg.CHSH_A
        b0, b1 = self._cfg.CHSH_B

        # calculate CHSH expression using the 4 expectation values
        E00 = self._expectation(a0, b0)
        E01 = self._expectation(a0, b1)
        E10 = self._expectation(a1, b0)
        E11 = self._expectation(a1, b1)
        chsh = abs(E00 - E01 + E10 + E11)

        # mark protocol as compromised if CHSH is not violated
        self._isKeyCompromised = chsh <= 2

        if self._isKeyCompromised:
            self._key = None
            self._isKeyValid = False
        else:
            # create the key
            key_array = np.array(bitsA_key, dtype=np.uint8)
            self._key = np.packbits(key_array).tobytes()
            self._isKeyValid = True

        return not self._isKeyCompromised


if __name__ == '__main__':
    pass
