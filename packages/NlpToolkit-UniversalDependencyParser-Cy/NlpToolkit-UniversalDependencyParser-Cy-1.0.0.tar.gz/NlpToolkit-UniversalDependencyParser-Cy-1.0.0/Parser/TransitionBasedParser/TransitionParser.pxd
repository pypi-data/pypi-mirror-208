from DependencyParser.Universal.UniversalDependencyTreeBankCorpus cimport UniversalDependencyTreeBankCorpus
from DependencyParser.Universal.UniversalDependencyTreeBankSentence cimport UniversalDependencyTreeBankSentence

from Parser.TransitionBasedParser.Agenda cimport Agenda
from Parser.TransitionBasedParser.Oracle cimport Oracle
from Parser.TransitionBasedParser.ScoringOracle cimport ScoringOracle
from Parser.TransitionBasedParser.State cimport State

cdef class TransitionParser:
    cpdef UniversalDependencyTreeBankSentence createResultSentence(self,
                                                                   UniversalDependencyTreeBankSentence universalDependencyTreeBankSentence)
    cpdef bint checkStates(self, Agenda agenda)
    cpdef simulateParseOnCorpus(self,
                              UniversalDependencyTreeBankCorpus corpus,
                              int windowSize)
    cpdef State initialState(self, UniversalDependencyTreeBankSentence sentence)
    cpdef list constructCandidates(self,
                            object transitionSystem,
                            State state)
    cpdef State dependencyParseWithBeamSearch(self,
                                      ScoringOracle oracle,
                                      int beamSize,
                                      UniversalDependencyTreeBankSentence universalDependencyTreeBankSentence,
                                      object transitionSystem)
    cpdef UniversalDependencyTreeBankCorpus dependencyParseCorpus(self,
                              UniversalDependencyTreeBankCorpus universalDependencyTreeBankCorpus,
                              Oracle oracle)
