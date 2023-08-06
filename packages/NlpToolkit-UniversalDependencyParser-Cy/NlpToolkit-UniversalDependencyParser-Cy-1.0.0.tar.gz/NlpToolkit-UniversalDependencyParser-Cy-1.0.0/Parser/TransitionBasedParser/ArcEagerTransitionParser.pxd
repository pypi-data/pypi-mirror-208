from DependencyParser.Universal.UniversalDependencyTreeBankSentence cimport UniversalDependencyTreeBankSentence

from Parser.TransitionBasedParser.Oracle cimport Oracle
from Parser.TransitionBasedParser.TransitionParser cimport TransitionParser

cdef class ArcEagerTransitionParser(TransitionParser):

    cpdef list simulateParse(self,
                      UniversalDependencyTreeBankSentence sentence,
                      int windowSize)
    cpdef UniversalDependencyTreeBankSentence dependencyParse(self,
                        UniversalDependencyTreeBankSentence universalDependencyTreeBankSentence,
                        Oracle oracle)
