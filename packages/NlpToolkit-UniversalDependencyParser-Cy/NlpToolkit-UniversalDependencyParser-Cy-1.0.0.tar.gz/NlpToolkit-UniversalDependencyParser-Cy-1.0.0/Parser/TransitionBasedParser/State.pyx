from DependencyParser.Universal.UniversalDependencyRelation cimport UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyTreeBankWord cimport UniversalDependencyTreeBankWord

from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.TransitionSystem import TransitionSystem

cdef class State:

    def __init__(self,
                 stack: list,
                 wordList: list,
                 relations: list):
        self.__stack = stack
        self.__word_list = wordList
        self.__relations = relations

    cpdef applyShift(self):
        if len(self.__word_list) > 0:
            self.__stack.append(self.__word_list.pop(0))

    cpdef applyLeftArc(self, object _type):
        if len(self.__stack) > 1:
            before_last = self.__stack[len(self.__stack) - 2].getWord()
            index = self.__stack[len(self.__stack) - 1].getToWord()
            before_last.setRelation(UniversalDependencyRelation(index, _type.name.replace("_", ":")))
            self.__stack.pop(len(self.__stack) - 2)
            self.__relations.append(StackRelation(before_last, UniversalDependencyRelation(index, _type.name.replace("_", ":"))))

    cpdef applyRightArc(self, object _type):
        if len(self.__stack) > 1:
            last = self.__stack[len(self.__stack) - 1].getWord()
            index = self.__word_list[0].getToWord()
            last.setRelation(UniversalDependencyRelation(index, _type.name.replace("_", ":")))
            self.__stack.pop()
            self.__relations.append(StackRelation(last, UniversalDependencyRelation(index, _type.name.replace("_", ":"))))

    cpdef applyArcEagerLeftArc(self, object _type):
        if len(self.__stack) > 0 and len(self.__word_list) > 0:
            last_element_of_stack = self.__stack[len(self.__stack) - 1].getWord()
            index = self.__word_list[0].getToWord()
            last_element_of_stack.setRelation(UniversalDependencyRelation(index, _type.name.replace("_", ":")))
            self.__stack.pop()
            self.__relations.append(StackRelation(last_element_of_stack, UniversalDependencyRelation(index, _type.name.replace("_", ":"))))

    cpdef applyArcEagerRightArc(self, object _type):
        if len(self.__stack) > 0 and len(self.__word_list) > 0:
            first_element_of_word_list = self.__word_list[0].getWord()
            index = self.__stack[len(self.__stack) - 1].getToWord()
            first_element_of_word_list.setRelation(UniversalDependencyRelation(index, _type.name.replace("_", ":")))
            self.applyShift()
            self.__relations.append(StackRelation(first_element_of_word_list, UniversalDependencyRelation(index, _type.name.replace("_", ":"))))

    cpdef applyReduce(self):
        if len(self.__stack) > 0:
            self.__stack.pop()

    cpdef apply(self, object command, object _type, object transitionSystem):
        if transitionSystem == TransitionSystem.ARC_STANDARD:
            if command == Command.LEFTARC:
                self.applyLeafArc(_type)
            elif command == Command.RIGHTARC:
                self.applyRightArc(_type)
            elif command == Command.SHIFT:
                self.applyShift()
        elif transitionSystem == TransitionSystem.ARC_EAGER:
            if command == Command.LEFTARC:
                self.applyArcEagerLeftArc(_type)
            elif command == Command.RIGHTARC:
                self.applyArcEagerRightArc(_type)
            elif command == Command.SHIFT:
                self.applyShift()
            elif command == Command.REDUCE:
                self.applyReduce()

    cpdef int relationSize(self):
        return len(self.__relations)

    cpdef int wordListSize(self):
        return len(self.__word_list)

    cpdef int stackSize(self):
        return len(self.__stack)

    cpdef UniversalDependencyTreeBankWord getStackWord(self, int index):
        size = len(self.__stack) - 1
        if size - index < 0:
            return None
        return self.__stack[size - index].getWord()

    cpdef UniversalDependencyTreeBankWord getPeek(self):
        if len(self.__stack) > 0:
            return self.__stack[len(self.__stack) - 1].getWord()
        return None

    cpdef UniversalDependencyTreeBankWord getWordListWord(self, int index):
        if index > len(self.__word_list) - 1:
            return None
        return self.__word_list[index].getWord()

    cpdef StackRelation getRelation(self, int index):
        if index < len(self.__relations):
            return self.__relations[index]
        return None
