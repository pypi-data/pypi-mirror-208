"""
A sample for including Cythonized tests file
"""
import unittest
from cytoolz.cytoolz_module import cytoolz_cpdeffunc, cytoolz_deffunc

# cdef-functions require cimport and .pxd file!
from cytoolz.cytoolz_module cimport cytoolz_cdeffunc


class CythonTestCase(unittest.TestCase):

    # IMPORTANT: in some reason Nose test doesn't recognize this module as a test
    def test_cytoolz_deffunc(self):
        self.assertEqual(3, cytoolz_deffunc(1, 2), 'simple addition')

    def test_cytoolz_cpdeffunc(self):
        self.assertEqual(3, cytoolz_cpdeffunc(1, 2), 'simple addition')

    def test_cytoolz_cdeffunc(self):
        self.assertEqual(3, cytoolz_cdeffunc(1, 2), 'simple addition')
