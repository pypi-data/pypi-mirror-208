"""
A sample for including Cythonized tests into test suite

Works with pytest, MAY NOT WORK WITH  nose
"""

import unittest
from sub.tests.test_my_template3_ import *

if __name__ == '__main__':
    unittest.main()
