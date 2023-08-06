from Corpus.Corpus cimport Corpus
from DependencyParser.ParserEvaluationScore cimport ParserEvaluationScore

cdef class UniversalDependencyTreeBankCorpus(Corpus):

    cdef str language
    cpdef constructor1(self, str fileName)
    cpdef ParserEvaluationScore compareParses(self, UniversalDependencyTreeBankCorpus corpus)
