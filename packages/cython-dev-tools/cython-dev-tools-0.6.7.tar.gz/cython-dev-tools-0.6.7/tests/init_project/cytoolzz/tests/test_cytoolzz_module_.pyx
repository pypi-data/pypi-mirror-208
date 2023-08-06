"""
A sample for including Cythonized tests file
"""
import unittest
from cytoolzz.cytoolzz_module import cytoolzz_cpdeffunc, cytoolzz_deffunc

# cdef-functions require cimport and .pxd file!
from cytoolzz.cytoolzz_module cimport cytoolzz_cdeffunc


class CythonTestCase(unittest.TestCase):

    # IMPORTANT: in some reason Nose test doesn't recognize this module as a test
    def test_cytoolzz_deffunc(self):
        self.assertEqual(3, cytoolzz_deffunc(1, 2), 'simple addition')

    def test_cytoolzz_cpdeffunc(self):
        self.assertEqual(3, cytoolzz_cpdeffunc(1, 2), 'simple addition')

    def test_cytoolzz_cdeffunc(self):
        self.assertEqual(3, cytoolzz_cdeffunc(1, 2), 'simple addition')
