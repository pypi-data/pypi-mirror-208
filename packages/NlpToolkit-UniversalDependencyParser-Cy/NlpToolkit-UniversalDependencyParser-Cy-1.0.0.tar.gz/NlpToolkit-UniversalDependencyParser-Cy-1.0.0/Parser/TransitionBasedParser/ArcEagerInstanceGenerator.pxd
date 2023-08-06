from Classification.Instance.Instance cimport Instance
from DependencyParser.Universal.UniversalDependencyTreeBankWord cimport UniversalDependencyTreeBankWord

from Parser.TransitionBasedParser.InstanceGenerator cimport InstanceGenerator
from Parser.TransitionBasedParser.State cimport State

cdef class ArcEagerInstanceGenerator(InstanceGenerator):

    cpdef bint suitable(self, UniversalDependencyTreeBankWord word)
    cpdef Instance generate(self,
                 State state,
                 int windowSize,
                 str command)
