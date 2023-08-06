cdef class DependencyRelation:

    cdef int to_word

    cpdef int to(self)
