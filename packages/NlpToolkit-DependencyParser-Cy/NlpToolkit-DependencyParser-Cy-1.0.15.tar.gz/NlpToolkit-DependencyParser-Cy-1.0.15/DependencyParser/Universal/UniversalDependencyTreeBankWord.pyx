from DependencyParser.Universal.UniversalDependencyPosType import UniversalDependencyPosType

cdef class UniversalDependencyTreeBankWord(Word):

    cpdef constructor1(self,
                     int id,
                     str lemma,
                     object upos,
                     str xpos,
                     UniversalDependencyTreeBankFeatures features,
                     UniversalDependencyRelation relation,
                     str deps,
                     str misc):
        self.id = id
        self.lemma = lemma
        self.u_pos = upos
        self.x_pos = xpos
        self.deps = deps
        self.features = features
        self.relation = relation
        self.misc = misc

    cpdef constructor2(self):
        self.id = 0
        self.lemma = ""
        self.u_pos = UniversalDependencyPosType.X
        self.x_pos = ""
        self.features = None
        self.deps = ""
        self.misc = ""
        self.relation = UniversalDependencyRelation()

    def __init__(self,
                 id: int = None,
                 name: str = None,
                 lemma: str = None,
                 upos: UniversalDependencyPosType = None,
                 xpos: str = None,
                 features: UniversalDependencyTreeBankFeatures = None,
                 relation: UniversalDependencyRelation = None,
                 deps: str = None,
                 misc: str = None):
        if id is not None:
            super().__init__(name)
            self.constructor1(id,
                              lemma,
                              upos,
                              xpos,
                              features,
                              relation,
                              deps,
                              misc)
        else:
            super().__init__("root")
            self.constructor2()

    cpdef int getId(self):
        return self.id

    cpdef str getLemma(self):
        return self.lemma

    cpdef object getUpos(self):
        return self.u_pos

    cpdef str getXPos(self):
        return self.x_pos

    cpdef UniversalDependencyTreeBankFeatures getFeatures(self):
        return self.features

    cpdef str getFeatureValue(self, str featureName):
        return self.features.getFeatureValue(featureName)

    cpdef bint featureExists(self, str featureName):
        return self.features.featureExists(featureName)

    cpdef UniversalDependencyRelation getRelation(self):
        return self.relation

    cpdef setRelation(self, UniversalDependencyRelation relation):
        self.relation = relation

    cpdef str getDeps(self):
        return self.deps

    cpdef str getMisc(self):
        return self.misc

    def __str__(self) -> str:
        return self.id.__str__() + "\t" + self.name + "\t" + self.lemma + "\t" + self.u_pos.__str__() + "\t" + \
               self.x_pos + "\t" + self.features.__str__() + "\t" + self.relation.to().__str__() + "\t" + \
               self.relation.__str__().lower() + "\t" + self.deps + "\t" + self.misc
