'''
/*****************/
/*   suite.py    */
/*  Version 1.0  */
/*   2025/03/29  */
/*****************/
'''
import unittest
import bb84_protocol_test
import no_encryption_test


def LoadTests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(bb84_protocol_test))
    suite.addTests(loader.loadTestsFromModule(no_encryption_test))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(LoadTests())
