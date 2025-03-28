'''
/**********************/
/* encryption_base.py */
/*    Version 1.0     */
/*     2025/03/23     */
/**********************/
'''
from abc import ABC, abstractmethod
import numpy as np


class EncryptionBase(ABC):
    def __init__(self):
        self._key = None
        self._isKeyValid = False
        self._isKeyCompromised = None
        self._protocol = None

    @abstractmethod
    def generateKey(self):
        pass

    @abstractmethod
    def reconcileKey(self):
        pass

    @property
    def key(self):
        return self._key

    @property
    def key_bits(self):
        return ''.join(format(byte, '08b') for byte in self._key)

    @property
    def protocol(self):
        return self._protocol

    def isKeyValid(self):
        return self._isKeyValid

    def isKeyCompromised(self):
        return self._isKeyCompromised

    def encrypt(self, message: str) -> bytes:
        if not self._isKeyValid:
            raise ValueError("Key is not valid")

        # Convert text to bytes
        message_bytes = message.encode()
        message_bits = np.unpackbits(
            np.frombuffer(message_bytes, dtype=np.uint8))
        key_bits = np.unpackbits(np.frombuffer(self._key, dtype=np.uint8))

        if len(message_bits) > len(key_bits):
            raise ValueError("Key is too short")
        # XOR the key and the message
        cipher_bits = np.bitwise_xor(message_bits,
                                     key_bits[:len(message_bits)])
        return np.packbits(cipher_bits).tobytes()

    def decrypt(self, cipher: bytes) -> str:
        # XOR again restores message
        if not self._isKeyValid:
            raise ValueError("Key is not valid")

        cipher_bits = np.unpackbits(np.frombuffer(cipher, dtype=np.uint8))
        key_bits = np.unpackbits(np.frombuffer(self._key, dtype=np.uint8))

        if len(cipher_bits) > len(key_bits):
            raise ValueError("Key is too short")

        message_bits = np.bitwise_xor(cipher_bits, key_bits[:len(cipher_bits)])
        message_bytes = np.packbits(message_bits).tobytes()
        # Convert bytes back to text
        return message_bytes.decode()


if __name__ == '__main__':
    pass
