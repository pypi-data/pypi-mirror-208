from abc import abstractmethod
from typing import List, Dict

from Classification.Model.Model import Model
from DependencyParser.Universal.UniversalDependencyRelation import UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyType import UniversalDependencyType

from Parser.TransitionBasedParser.Candidate import Candidate
from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.Decision import Decision
from Parser.TransitionBasedParser.State import State
from Parser.TransitionBasedParser.TransitionSystem import TransitionSystem


class Oracle:
    command_model: Model
    window_size: int

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

    def findBestValidEagerClassInfo(self,
                                    probabilities: Dict[str, float],
                                    state: State) -> str:
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

    def findBestValidStandardClassInfo(self,
                                       probabilities: Dict[str, float],
                                       state: State) -> str:
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

    def getDecisionCandidate(self, best: str) -> Candidate:
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
