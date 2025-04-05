'''
/*****************/
/*   suite.py    */
/*  Version 2.0  */
/*   2025/04/05  */
/*****************/
'''
import unittest
import no_encryption_test
import bb84_protocol_test
import e91_protocol_test


def LoadTests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(no_encryption_test))
    suite.addTests(loader.loadTestsFromModule(bb84_protocol_test))
    suite.addTests(loader.loadTestsFromModule(e91_protocol_test))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(LoadTests())
