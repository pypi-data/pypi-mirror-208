from DependencyParser.Universal.UniversalDependencyTreeBankWord cimport UniversalDependencyTreeBankWord

cdef class StackWord:

    cpdef constructor1(self):
        self.__word = UniversalDependencyTreeBankWord()
        self.__to_word = 0

    cpdef constructor2(self, UniversalDependencyTreeBankWord word, int toWord):
        self.__word = word
        self.__to_word = toWord

    def __init__(self,
                 word: UniversalDependencyTreeBankWord = None,
                 toWord: int = None):
        if word is None:
            self.constructor1()
        else:
            self.constructor2(word, toWord)

    cpdef UniversalDependencyTreeBankWord getWord(self):
        return self.__word

    cpdef int getToWord(self):
        return self.__to_word
