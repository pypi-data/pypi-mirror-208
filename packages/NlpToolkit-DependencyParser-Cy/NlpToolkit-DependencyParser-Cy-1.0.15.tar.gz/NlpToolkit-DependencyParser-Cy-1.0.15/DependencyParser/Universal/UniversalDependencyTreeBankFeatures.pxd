cdef class UniversalDependencyTreeBankFeatures:

    cdef dict feature_list

    cpdef str getFeatureValue(self, str feature)

    cpdef bint featureExists(self, str feature)
