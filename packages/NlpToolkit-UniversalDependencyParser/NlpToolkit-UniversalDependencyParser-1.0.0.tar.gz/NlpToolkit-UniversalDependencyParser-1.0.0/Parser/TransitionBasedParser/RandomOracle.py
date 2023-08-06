import random
from typing import List

from Classification.Model.Model import Model
from DependencyParser.Universal.UniversalDependencyRelation import UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyType import UniversalDependencyType

from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.Decision import Decision
from Parser.TransitionBasedParser.Oracle import Oracle
from Parser.TransitionBasedParser.State import State
from Parser.TransitionBasedParser.TransitionSystem import TransitionSystem


class RandomOracle(Oracle):

    def __init__(self,
                 model: Model,
                 windowSize: int):
        super().__init__(model, windowSize)

    def makeDecision(self, state: State) -> Decision:
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

    def scoreDecisions(self,
                       state: State,
                       transitionSystem: TransitionSystem) -> List[Decision]:
        return None
