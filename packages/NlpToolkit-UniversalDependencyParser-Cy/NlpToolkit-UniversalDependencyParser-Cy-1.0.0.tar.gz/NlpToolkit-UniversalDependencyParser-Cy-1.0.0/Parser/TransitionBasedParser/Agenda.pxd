from Parser.TransitionBasedParser.ScoringOracle cimport ScoringOracle
from Parser.TransitionBasedParser.State cimport State

cdef class Agenda:

    cdef dict __agenda
    cdef int __beam_size

    cpdef list getKeySet(self)
    cpdef updateAgenda(self,
                     ScoringOracle oracle,
                     State current)
    cpdef State best(self)
