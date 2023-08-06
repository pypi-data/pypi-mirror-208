from Parser.TransitionBasedParser.Decision cimport Decision
from Parser.TransitionBasedParser.Oracle cimport Oracle
from Parser.TransitionBasedParser.State cimport State

cdef class ArcEagerOracle(Oracle):
    cpdef Decision makeDecision(self, State state)
    cpdef dict scoreDecisions(self,
                              State state,
                              object transitionSystem)
