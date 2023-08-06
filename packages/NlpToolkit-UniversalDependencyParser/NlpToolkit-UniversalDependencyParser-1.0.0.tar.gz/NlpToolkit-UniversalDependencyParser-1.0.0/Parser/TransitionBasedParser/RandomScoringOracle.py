import random

from Parser.TransitionBasedParser.ScoringOracle import ScoringOracle
from Parser.TransitionBasedParser.State import State


class RandomScoringOracle(ScoringOracle):

    def score(self, state: State) -> float:
        return random.random()
