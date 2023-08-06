from abc import abstractmethod

from Parser.TransitionBasedParser.State import State


class ScoringOracle:

    @abstractmethod
    def score(self, state: State):
        pass
