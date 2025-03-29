'''
/*********************/
/* qubit_utils.py.py */
/*    Version 1.0    */
/*     2025/03/29    */
/*********************/
'''
import numpy as np


def ket0():
    # Define computational basis states
    return np.array([[1], [0]], dtype=complex)


def ket1():
    return np.array([[0], [1]], dtype=complex)


def tensor(a, b):
    # Tensor product for multi-qubit systems
    return np.kron(a, b)


def normalize(vec):
    # Normalize a quantum state vector
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def observable(theta_deg):
    # Observable defined as cos(θ)·X + sin(θ)·Z
    theta = np.deg2rad(theta_deg)
    return np.cos(theta) * np.array([[0, 1], [1, 0]], dtype=complex) + \
        np.sin(theta) * np.array([[1, 0], [0, -1]], dtype=complex)


def eigenstates(theta_deg):
    # Return eigenstates (normalized) of the above observable
    obs = observable(theta_deg)
    _, eigvecs = np.linalg.eigh(obs)
    return normalize(eigvecs[:, 0:1]), normalize(eigvecs[:, 1:2])


def measureQubit(state, theta_deg):
    # Perform a measurement of a single-qubit state in a basis defined by θ
    obs = observable(theta_deg)
    _, eigvecs = np.linalg.eigh(obs)
    # orthonormal eigenstates
    basis = [eigvecs[:, 0:1], eigvecs[:, 1:2]]
    # projection probabilities
    probs = [np.abs(b.conj().T @ state)[0, 0]**2 for b in basis]
    # remove small negative due to floating point
    probs = [max(0.0, np.real(p)) for p in probs]
    total = sum(probs)
    # normalize to 1.0
    probs = [p / total if total > 0 else 0.5 for p in probs]
    # simulate measurement
    outcome = np.random.choice([0, 1], p=probs)
    return outcome, basis[outcome]


if __name__ == '__main__':
    pass
