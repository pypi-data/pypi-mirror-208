cdef class ParserEvaluationScore:

    def __init__(self, float LAS = 0.0, float UAS = 0.0, float LS = 0.0, int wordCount = 0):
        self.LAS = LAS
        self.UAS = UAS
        self.LS = LS
        self.word_count = wordCount

    cpdef float getLS(self):
        return self.LS

    cpdef float getLAS(self):
        return self.LAS

    cpdef float getUAS(self):
        return self.UAS

    cpdef int getWordCount(self):
        return self.word_count

    cpdef add(self, ParserEvaluationScore parserEvaluationScore):
        self.LAS = (self.LAS * self.word_count + parserEvaluationScore.LAS * parserEvaluationScore.word_count) / \
                   (self.word_count + parserEvaluationScore.word_count)
        self.UAS = (self.UAS * self.word_count + parserEvaluationScore.UAS * parserEvaluationScore.word_count) / \
                   (self.word_count + parserEvaluationScore.word_count)
        self.LS = (self.LS * self.word_count + parserEvaluationScore.LS * parserEvaluationScore.word_count) / \
                  (self.word_count + parserEvaluationScore.word_count)
        self.word_count += parserEvaluationScore.word_count
