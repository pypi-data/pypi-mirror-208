from Parser.TransitionBasedParser.Candidate cimport Candidate

cdef class Decision(Candidate):

    cdef float __point

    cpdef float getPoint(self)
