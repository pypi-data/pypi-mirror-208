from DependencyParser.Universal.UniversalDependencyTreeBankWord cimport UniversalDependencyTreeBankWord

from Parser.TransitionBasedParser.StackRelation cimport StackRelation
from Parser.TransitionBasedParser.StackWord cimport StackWord

cdef class State:

    cdef list __stack
    cdef list __word_list
    cdef list __relations

    cpdef applyShift(self)
    cpdef applyLeftArc(self, object _type)
    cpdef applyRightArc(self, object _type)
    cpdef applyArcEagerLeftArc(self, object _type)
    cpdef applyArcEagerRightArc(self, object _type)
    cpdef applyReduce(self)
    cpdef apply(self, object command, object _type, object transitionSystem)
    cpdef int relationSize(self)
    cpdef int wordListSize(self)
    cpdef int stackSize(self)
    cpdef UniversalDependencyTreeBankWord getStackWord(self, int index)
    cpdef UniversalDependencyTreeBankWord getPeek(self)
    cpdef UniversalDependencyTreeBankWord getWordListWord(self, int index)
    cpdef StackRelation getRelation(self, int index)
