"""
A sample for including Cythonized tests into test suite

Works with pytest, MAY NOT WORK WITH  nose
"""

import unittest
from cytoolz.tests.test_cytoolz_module_ import *

if __name__ == '__main__':
    unittest.main()
