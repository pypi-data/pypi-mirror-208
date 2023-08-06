from DependencyParser.DependencyRelation cimport DependencyRelation


cdef class StanfordDependencyRelation(DependencyRelation):

    cdef object __stanford_dependency_type
