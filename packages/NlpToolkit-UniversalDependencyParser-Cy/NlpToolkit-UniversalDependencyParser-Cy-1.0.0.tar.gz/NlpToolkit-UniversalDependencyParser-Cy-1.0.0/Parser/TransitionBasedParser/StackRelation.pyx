from DependencyParser.Universal.UniversalDependencyRelation cimport UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyTreeBankWord cimport UniversalDependencyTreeBankWord

cdef class StackRelation:

    def __init__(self,
                 word: UniversalDependencyTreeBankWord,
                 relation: UniversalDependencyRelation):
        self.__word = word
        self.__relation = relation

    cpdef UniversalDependencyTreeBankWord getWord(self):
        return self.__word

    cpdef UniversalDependencyRelation getRelation(self):
        return self.__relation
