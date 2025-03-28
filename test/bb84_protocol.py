'''
/********************/
/*    unittest      */
/* bb84_protocol.py */
/*   Version 1.0    */
/*    2025/03/27    */
/********************/
'''
import json
import os
import sys
from types import SimpleNamespace
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))
from encryptlib import BB84Protocol  # noqa

with open('config.json', 'r') as f:
    cfg = json.load(f, object_hook=lambda d: SimpleNamespace(**d))


class TestNoEncryption(unittest.TestCase):
    def setUp(self):
        self.enc = BB84Protocol(cfg.BB84Protocol)

    def test_protocol(self):
        EXPECTED = 'BB84 Protocol'
        COMPUTED = self.enc.protocol
        self.assertEqual(COMPUTED, EXPECTED)

    def test_generate_key(self):
        self.enc.generateKey(seed=71107)
        self.assertFalse(self.enc.isKeyValid())

    def test_generate_valid_key(self):
        self.enc.generateKey()
        self.assertFalse(self.enc.isKeyValid())
        self.enc.sendKey()
        self.enc.reconcileKey()
        self.assertTrue(self.enc.isKeyValid())

    def test_generate_eavesdropped_key(self):
        self.enc.generateKey()
        self.assertFalse(self.enc.isKeyValid())
        self.enc.sendKey(True)
        self.enc.reconcileKey()
        self.assertFalse(self.enc.isKeyValid())

    def test_encode_message(self):
        self.enc.generateKey(seed=18353)
        EXPECTED = 'This is a test message'
        self.enc.sendKey()
        self.enc.reconcileKey()
        message = self.enc.encrypt(EXPECTED)
        message_bits = ''.join(format(byte, '08b') for byte in message)
        self.assertEqual(message_bits[0:16], '0110101100110111')
        COMPUTED = self.enc.decrypt(message)
        self.assertEqual(COMPUTED, EXPECTED)

    def test_encode_eavesdropped_message(self):
        self.enc.generateKey(seed=18353)
        EXPECTED = 'This is a test message'
        self.enc.sendKey(True)
        self.enc.reconcileKey()
        with self.assertRaises(ValueError):
            self.enc.encrypt(EXPECTED)


if __name__ == '__main__':
    unittest.main()
