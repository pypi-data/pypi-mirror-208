from abc import abstractmethod

from Parser.TransitionBasedParser.State cimport State

cdef class ScoringOracle:

    @abstractmethod
    def score(self, state: State):
        pass
