# cython: language_level=3
import cython

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef get_mu(buffer_):
    cdef int buffer = buffer_
    cdef int multi = 8*512
    cdef int multi2 = multi
    cdef int buffer2

    if buffer > 512 * multi:
        buffer2 = 512 * multi

        while (buffer % buffer2 != 0) and multi > 2:
            multi -= 2
            buffer2 = 512 * multi

        if multi > 0:
            buffer = buffer2
        else:
            buffer = 512*4
    if buffer < 512:
        buffer = 512
    return buffer
