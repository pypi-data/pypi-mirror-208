from Corpus.Sentence cimport Sentence
from DependencyParser.ParserEvaluationScore cimport ParserEvaluationScore

cdef class UniversalDependencyTreeBankSentence(Sentence):

    cdef list comments

    cpdef addComment(self, str comment)
    cpdef ParserEvaluationScore compareParses(self, UniversalDependencyTreeBankSentence sentence)
