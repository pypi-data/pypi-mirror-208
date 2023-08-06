import re
from xml.etree.ElementTree import Element

cdef class TurkishDependencyTreeBankWord(Word):

    def __init__(self, wordNode: Element):
        """
        Given the parsed xml node which contains information about a word and related attributes including the
        dependencies, the method constructs a {@link TurkishDependencyTreeBankWord} from it.

        PARAMETERS
        -----------
        wordNode : Element
            Xml parsed node containing information about a word.
        """
        cdef int to_word, to_ig, index, i
        cdef str ig, relation_name, part
        to_word = 0
        to_ig = 0
        self.__original_parses = []
        self.name = wordNode.text
        ig = wordNode.attrib["IG"]
        ig = ig[:ig.index("+")] + "+" + ig[ig.index("+") + 1:].upper()
        self.__parse = MorphologicalParse(self.splitIntoInflectionalGroups(ig))
        self.__relation = None
        relation_name = wordNode.attrib["REL"]
        if relation_name != "[,( )]":
            relation_parts = re.compile("[\\[()\\],]").split(relation_name)
            index = 0
            for part in relation_parts:
                if len(part) != 0:
                    index = index + 1
                    if index == 1:
                        to_word = int(part)
                    elif index == 2:
                        to_ig = int(part)
                    elif index == 3:
                        self.__relation = TurkishDependencyRelation(to_word - 1, to_ig - 1, part)
        for i in range(1, 10):
            if ("ORG_ID" + str(i)) in wordNode.attrib:
                ig = wordNode.attrib["ORG_ID" + str(i)]
                ig = ig[:ig.index("+")] + "+" + ig[ig.index("+") + 1:].upper()
                self.__original_parses.append(MorphologicalParse(self.splitIntoInflectionalGroups(ig)))

    cpdef list splitIntoInflectionalGroups(self, str IG):
        """
        Given the morphological parse of a word, this method splits it into inflectional groups.

        PARAMETERS
        ----------
        IG : str
            Morphological parse of the word in string form.

        RETURNS
        -------
        list
            A list of inflectional groups stored as strings.
        """
        cdef list inflectional_groups
        cdef str part
        inflectional_groups = []
        IG = IG.replace("(+Punc", "@").replace(")+Punc", "$")
        IGs = re.compile("[\\[()\\]]").split(IG)
        for part in IGs:
            part = part.replace("@", "(+Punc").replace("$", ")+Punc")
            if len(part) != 0:
                inflectional_groups.append(part)
        return inflectional_groups

    cpdef MorphologicalParse getParse(self):
        """
        Accessor for the parse attribute

        RETURNS
        -------
        MorphologicalPArse
            Parse attribute
        """
        return self.__parse

    cpdef MorphologicalParse getOriginalParse(self, int index):
        """
        Accessor for a specific parse.

        PARAMETERS
        ----------
        index : int
            Index of the word.

        RETURNS
        -------
        MorphologicalParse
            Parse of the index'th word
        """
        if index < len(self.__original_parses):
            return self.__original_parses[index]
        else:
            return None

    cpdef int size(self):
        """
        Number of words in this item.

        RETURNS
        -------
        int
            Number of words in this item.
        """
        return len(self.__original_parses)

    cpdef TurkishDependencyRelation getRelation(self):
        """
        Accessor for the relation attribute.

        RETURNS
        -------
        TurkishDependencyRelation
            relation attribute.
        """
        return self.__relation

    def __repr__(self):
        return f"{self.name} {self.__parse} {self.__original_parses} {self.__relation}"
