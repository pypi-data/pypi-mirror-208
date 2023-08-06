from Classification.Model.Model cimport Model

from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.SimpleInstanceGenerator cimport SimpleInstanceGenerator

cdef class ArcEagerOracle(Oracle):

    def __init__(self,
                 model: Model,
                 windowSize: int):
        super().__init__(model, windowSize)

    cpdef Decision makeDecision(self, State state):
        instanceGenerator = SimpleInstanceGenerator()
        instance = instanceGenerator.generate(state, self.window_size, "")
        best = self.findBestValidEagerClassInfo(self.command_model.predictProbability(instance), state)
        decisionCandidate = self.getDecisionCandidate(best)
        if decisionCandidate.getCommand() == Command.SHIFT:
            return Decision(Command.SHIFT, None, 0.0)
        elif decisionCandidate.getCommand() == Command.REDUCE:
            return Decision(Command.REDUCE, None, 0.0)
        else:
            return Decision(decisionCandidate.getCommand(), decisionCandidate.getUniversalDependencyType(), 0.0)

    cpdef dict scoreDecisions(self,
                              State state,
                              object transitionSystem):
        return None
