from Corpus.Corpus cimport Corpus
from DataStructure.CounterHashMap cimport CounterHashMap

from DependencyParser.ParserEvaluationScore cimport ParserEvaluationScore
from DependencyParser.Universal.UniversalDependencyTreeBankSentence cimport UniversalDependencyTreeBankSentence

cdef class UniversalDependencyTreeBankCorpus(Corpus):

    cpdef constructor1(self, str fileName):
        cdef list lines
        cdef str line, sentence
        self.sentences = []
        self.paragraphs = []
        self.word_list = CounterHashMap()
        if '/' in fileName:
            self.language = fileName[fileName.index('/') + 1:fileName.index('_')]
        else:
            self.language = fileName[0:fileName.index('_')]
        sentence = ""
        file = open(fileName, "r")
        lines = file.readlines()
        file.close()
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                self.addSentence(UniversalDependencyTreeBankSentence(self.language, sentence))
                sentence = ""
            else:
                sentence = sentence + line + "\n"

    def __init__(self, fileName: str = None):
        if fileName is not None:
            self.constructor1(fileName)

    cpdef ParserEvaluationScore compareParses(self, UniversalDependencyTreeBankCorpus corpus):
        score = ParserEvaluationScore()
        for i in range(len(self.sentences)):
            score.add(self.sentences[i].compareParses(corpus.getSentence(i)))
        return score
