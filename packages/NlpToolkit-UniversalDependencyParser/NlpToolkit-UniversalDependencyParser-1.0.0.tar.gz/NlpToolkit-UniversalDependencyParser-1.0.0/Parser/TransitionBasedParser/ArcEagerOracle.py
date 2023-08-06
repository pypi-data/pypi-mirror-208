from typing import List

from Classification.Model.Model import Model

from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.Decision import Decision
from Parser.TransitionBasedParser.Oracle import Oracle
from Parser.TransitionBasedParser.SimpleInstanceGenerator import SimpleInstanceGenerator
from Parser.TransitionBasedParser.State import State
from Parser.TransitionBasedParser.TransitionSystem import TransitionSystem


class ArcEagerOracle(Oracle):

    def __init__(self,
                 model: Model,
                 windowSize: int):
        super().__init__(model, windowSize)

    def makeDecision(self, state: State) -> Decision:
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

    def scoreDecisions(self,
                       state: State,
                       transitionSystem: TransitionSystem) -> List[Decision]:
        return None
