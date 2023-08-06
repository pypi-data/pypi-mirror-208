from DependencyParser.DependencyRelation cimport DependencyRelation
from DependencyParser.ParserEvaluationScore cimport ParserEvaluationScore

cdef class UniversalDependencyRelation(DependencyRelation):

    cdef object __universal_dependency_type
    cpdef constructor1(self, str dependencyType)
    cpdef constructor2(self)
    cpdef ParserEvaluationScore compareRelations(self, UniversalDependencyRelation relation)
