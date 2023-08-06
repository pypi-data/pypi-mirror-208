from Classification.Instance.Instance cimport Instance

from Parser.TransitionBasedParser.InstanceGenerator cimport InstanceGenerator
from Parser.TransitionBasedParser.State cimport State

cdef class SimpleInstanceGenerator(InstanceGenerator):

    cpdef Instance generate(self,
                            State state,
                            int windowSize,
                            str command)
