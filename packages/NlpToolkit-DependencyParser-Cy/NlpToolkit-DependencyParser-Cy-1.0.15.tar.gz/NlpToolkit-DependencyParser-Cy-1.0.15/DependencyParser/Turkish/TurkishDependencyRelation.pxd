from DependencyParser.DependencyRelation cimport DependencyRelation


cdef class TurkishDependencyRelation(DependencyRelation):

    cdef int __to_ig
    cdef object __turkish_dependency_type

    cpdef int toIG(self)
    cpdef object getTurkishDependencyType(self)
