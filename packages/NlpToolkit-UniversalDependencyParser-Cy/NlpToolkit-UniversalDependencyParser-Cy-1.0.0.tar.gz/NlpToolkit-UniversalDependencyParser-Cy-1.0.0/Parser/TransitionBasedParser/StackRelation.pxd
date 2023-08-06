from DependencyParser.Universal.UniversalDependencyRelation cimport UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyTreeBankWord cimport UniversalDependencyTreeBankWord

cdef class StackRelation:

    cdef UniversalDependencyTreeBankWord __word
    cdef UniversalDependencyRelation __relation

    cpdef UniversalDependencyTreeBankWord getWord(self)
    cpdef UniversalDependencyRelation getRelation(self)
