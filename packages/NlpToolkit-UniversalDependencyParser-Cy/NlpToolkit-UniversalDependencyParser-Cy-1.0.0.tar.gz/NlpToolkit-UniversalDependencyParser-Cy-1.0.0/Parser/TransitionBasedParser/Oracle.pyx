from abc import abstractmethod
from typing import List

from Classification.Model.Model cimport Model
from DependencyParser.Universal.UniversalDependencyRelation cimport UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyType import UniversalDependencyType

from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.Decision cimport Decision
from Parser.TransitionBasedParser.TransitionSystem import TransitionSystem

cdef class Oracle:

    def __init__(self,
                 model: Model,
                 window_size: int):
        self.command_model = model
        self.window_size = window_size

    @abstractmethod
    def makeDecision(self, state: State) -> Decision:
        pass

    @abstractmethod
    def scoreDecisions(self,
                       state: State,
                       transitionSystem: TransitionSystem) -> List[Decision]:
        pass

    cpdef str findBestValidEagerClassInfo(self,
                                          dict probabilities,
                                          State state):
        best_value = 0.0
        best = ""
        for key in probabilities:
            if probabilities[key] > best_value:
                if key == "SHIFT" or key == "RIGHTARC":
                    if state.wordListSize() > 0:
                        best = key
                        best_value = probabilities[key]
                    elif state.stackSize() > 1:
                        if not (key == "REDUCE" and state.getPeek().getRelation() is None):
                            best = key
                            best_value = probabilities[key]
        return best

    cpdef str findBestValidStandardClassInfo(self,
                                             dict probabilities,
                                             State state):
        best_value = 0.0
        best = ""
        for key in probabilities:
            if probabilities[key] > best_value:
                if key == "SHIFT":
                    if state.wordListSize() > 0:
                        best = key
                        best_value = probabilities[key]
                    elif state.stackSize() > 1:
                        best = key
                        best_value = probabilities[key]
        return best

    cpdef Candidate getDecisionCandidate(self, str best):
        if "(" in best:
            command = best[0:best.index('(')]
            relation = best[best.index('(') + 1:best.index(')')]
            _type = UniversalDependencyRelation.getDependencyTag(relation)
        else:
            command = best
            _type = UniversalDependencyType.DEP
        if command == "SHIFT":
            return Candidate(Command.SHIFT, _type)
        elif command == "REDUCE":
            return Candidate(Command.REDUCE, _type)
        elif command == "LEFTARC":
            return Candidate(Command.LEFTARC, _type)
        elif command == "RIGHTARC":
            return Candidate(Command.RIGHTARC, _type)
        return None
