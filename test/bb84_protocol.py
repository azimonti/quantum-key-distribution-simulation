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


if __name__ == '__main__':
    unittest.main()
