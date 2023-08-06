from Dictionary.Word cimport Word
from MorphologicalAnalysis.MorphologicalParse cimport MorphologicalParse
from DependencyParser.Turkish.TurkishDependencyRelation cimport TurkishDependencyRelation


cdef class TurkishDependencyTreeBankWord(Word):

    cdef MorphologicalParse __parse
    cdef list __original_parses
    cdef TurkishDependencyRelation __relation

    cpdef list splitIntoInflectionalGroups(self, str IG)
    cpdef MorphologicalParse getParse(self)
    cpdef MorphologicalParse getOriginalParse(self, int index)
    cpdef int size(self)
    cpdef TurkishDependencyRelation getRelation(self)
