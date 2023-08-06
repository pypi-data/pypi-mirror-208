"""
A sample for including Cythonized tests into test suite

Works with pytest, MAY NOT WORK WITH  nose
"""

import unittest
from cytoolzz.tests.test_cytoolzz_module_ import *

if __name__ == '__main__':
    unittest.main()
