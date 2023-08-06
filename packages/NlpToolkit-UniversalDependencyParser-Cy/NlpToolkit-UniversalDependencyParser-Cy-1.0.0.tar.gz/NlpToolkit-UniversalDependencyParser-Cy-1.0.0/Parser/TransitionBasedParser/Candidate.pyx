from DependencyParser.Universal.UniversalDependencyRelation import UniversalDependencyType

from Parser.TransitionBasedParser.Command import Command

cdef class Candidate:

    def __init__(self,
                 command: Command,
                 universalDependencyType: UniversalDependencyType):
        self.__command = command
        self.__universal_dependency_type = universalDependencyType

    cpdef object getCommand(self):
        return self.__command

    cpdef object getUniversalDependencyType(self):
        return self.__universal_dependency_type
