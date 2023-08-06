from Parser.TransitionBasedParser.ScoringOracle cimport ScoringOracle
from Parser.TransitionBasedParser.State cimport State

cdef class RandomScoringOracle(ScoringOracle):

    cpdef float score(self, State state)