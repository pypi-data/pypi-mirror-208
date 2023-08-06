from random import random

from Classification.Model.Model cimport Model
from DependencyParser.Universal.UniversalDependencyRelation cimport UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyType import UniversalDependencyType

from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.TransitionSystem import TransitionSystem

cdef class RandomOracle(Oracle):

    def __init__(self,
                 model: Model,
                 windowSize: int):
        super().__init__(model, windowSize)

    cpdef Decision makeDecision(self, State state):
        command = random.randrange(3)
        relation = random.randrange(len(UniversalDependencyRelation.universal_dependency_tags))
        if command == 0:
            return Decision(Command.LEFTARC, UniversalDependencyRelation.universal_dependency_tags[relation], 0)
        elif command == 1:
            return Decision(Command.RIGHTARC, UniversalDependencyRelation.universal_dependency_tags[relation], 0)
        elif command == 2:
            return Decision(Command.SHIFT, UniversalDependencyType.DEP, 0)
        else:
            return None

    cpdef list scoreDecisions(self,
                              State state,
                              object transitionSystem):
        return None
