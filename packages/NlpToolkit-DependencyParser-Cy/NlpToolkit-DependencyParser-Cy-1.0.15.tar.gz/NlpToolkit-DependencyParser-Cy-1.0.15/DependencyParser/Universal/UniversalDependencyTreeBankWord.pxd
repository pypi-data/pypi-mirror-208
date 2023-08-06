from Dictionary.Word cimport Word
from DependencyParser.Universal.UniversalDependencyRelation cimport UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyTreeBankFeatures cimport UniversalDependencyTreeBankFeatures


cdef class UniversalDependencyTreeBankWord(Word):

    cdef int id
    cdef str lemma
    cdef object u_pos
    cdef str x_pos
    cdef UniversalDependencyTreeBankFeatures features
    cdef UniversalDependencyRelation relation
    cdef str deps
    cdef str misc

    cpdef int getId(self)
    cpdef str getLemma(self)
    cpdef object getUpos(self)
    cpdef str getXPos(self)
    cpdef UniversalDependencyTreeBankFeatures getFeatures(self)
    cpdef str getFeatureValue(self, str featureName)
    cpdef bint featureExists(self, str featureName)
    cpdef setRelation(self, UniversalDependencyRelation relation)
    cpdef UniversalDependencyRelation getRelation(self)
    cpdef str getDeps(self)
    cpdef str getMisc(self)
    cpdef constructor1(self,
                       int id,
                       str lemma,
                       object upos,
                       str xpos,
                       UniversalDependencyTreeBankFeatures features,
                       UniversalDependencyRelation relation,
                       str deps,
                       str misc)
    cpdef constructor2(self)
