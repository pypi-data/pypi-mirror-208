from DependencyParser.Universal.UniversalDependencyTreeBankWord cimport UniversalDependencyTreeBankWord

cdef class StackWord:

    cdef UniversalDependencyTreeBankWord __word
    cdef int __to_word

    cpdef constructor1(self)
    cpdef constructor2(self, UniversalDependencyTreeBankWord word, int toWord)
    cpdef UniversalDependencyTreeBankWord getWord(self)
    cpdef int getToWord(self)
