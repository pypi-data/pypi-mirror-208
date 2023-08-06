from Corpus.Sentence cimport Sentence


cdef class TurkishDependencyTreeBankSentence(Sentence):

    cpdef int maxDependencyLength(self)
