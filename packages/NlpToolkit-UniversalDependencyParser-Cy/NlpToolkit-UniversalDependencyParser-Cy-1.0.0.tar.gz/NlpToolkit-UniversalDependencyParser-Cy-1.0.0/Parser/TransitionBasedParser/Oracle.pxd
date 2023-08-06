from Classification.Model.Model cimport Model

from Parser.TransitionBasedParser.Candidate cimport Candidate
from Parser.TransitionBasedParser.State cimport State

cdef class Oracle:
    cdef Model command_model
    cdef int window_size

    cpdef str findBestValidEagerClassInfo(self,
                                          dict probabilities,
                                          State state)
    cpdef str findBestValidStandardClassInfo(self,
                                            dict probabilities,
                                            State state)
    cpdef Candidate getDecisionCandidate(self, str best)
