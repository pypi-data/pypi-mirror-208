"""
Samples cython Module
"""
cdef cytoolz_cdeffunc(int a, int b):
    return a + b

cpdef cytoolz_cpdeffunc(int a, int b):
    return a + b

def cytoolz_deffunc(int a, int b):
    return a + b
