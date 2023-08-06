import xml

from Corpus.Corpus cimport Corpus

from DependencyParser.Turkish.TurkishDependencyTreeBankSentence cimport TurkishDependencyTreeBankSentence


cdef class TurkishDependencyTreeBankCorpus(Corpus):

    def __init__(self, fileName: str = None):
        """
        Empty constructor for TurkishDependencyTreeBankCorpus. Initializes the sentences and wordList attributes.
        """
        super().__init__()
        if fileName is not None:
            root = xml.etree.ElementTree.parse(fileName).getroot()
            for sentence_node in root:
                sentence = TurkishDependencyTreeBankSentence(sentence_node)
                self.sentences.append(sentence)

    cpdef TurkishDependencyTreeBankCorpus emptyCorpus(self):
        """
        Constructor to create an empty copy of this corpus.

        RETURNS
        -------
        TurkishDependencyTreeBankCorpus
            An empty copy of this corpus.
        """
        return TurkishDependencyTreeBankCorpus()
