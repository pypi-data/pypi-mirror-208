from DependencyParser.Universal.UniversalDependencyRelation import UniversalDependencyType

from Parser.TransitionBasedParser.Candidate cimport Candidate
from Parser.TransitionBasedParser.Command import Command

cdef class Decision(Candidate):

    def __init__(self,
                 command: Command,
                 relation: UniversalDependencyType,
                 point: float):
        super().__init__(command, relation)
        self.__point = point

    cpdef float getPoint(self):
        return self.__point
