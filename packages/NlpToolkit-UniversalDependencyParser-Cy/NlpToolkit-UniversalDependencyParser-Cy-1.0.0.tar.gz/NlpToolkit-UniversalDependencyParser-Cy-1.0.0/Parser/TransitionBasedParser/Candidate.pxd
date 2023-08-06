cdef class Candidate(object):

    cdef object __command
    cdef object __universal_dependency_type

    cpdef object getCommand(self)
    cpdef object getUniversalDependencyType(self)
