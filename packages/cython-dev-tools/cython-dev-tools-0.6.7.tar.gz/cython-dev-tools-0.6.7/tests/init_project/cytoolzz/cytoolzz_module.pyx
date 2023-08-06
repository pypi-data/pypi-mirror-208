"""
Samples cython Module
"""
cdef cytoolzz_cdeffunc(int a, int b):
    return a + b

cpdef cytoolzz_cpdeffunc(int a, int b):
    return a + b

def cytoolzz_deffunc(int a, int b):
    return a + b
