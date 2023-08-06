from DependencyParser.Universal.UniversalDependencyTreeBankSentence cimport UniversalDependencyTreeBankSentence

from Parser.TransitionBasedParser.Oracle cimport Oracle
from Parser.TransitionBasedParser.TransitionParser cimport TransitionParser

cdef class ArcStandardTransitionParser(TransitionParser):
    cpdef bint checkForMoreRelation(self,
                                    list wordList,
                                    int _id)
    cpdef list simulateParse(self,
                      UniversalDependencyTreeBankSentence sentence,
                      int windowSize)
    cpdef UniversalDependencyTreeBankSentence dependencyParse(self,
                        UniversalDependencyTreeBankSentence universalDependencyTreeBankSentence,
                        Oracle oracle)
