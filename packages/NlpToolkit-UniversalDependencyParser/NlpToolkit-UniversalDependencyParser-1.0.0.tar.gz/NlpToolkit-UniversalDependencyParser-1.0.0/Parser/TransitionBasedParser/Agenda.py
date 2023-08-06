import sys
from typing import Dict, List

from Parser.TransitionBasedParser.ScoringOracle import ScoringOracle
from Parser.TransitionBasedParser.State import State


class Agenda:

    __agenda: Dict[State, float]
    __beam_size: int

    def __init__(self, beamSize: int):
        self.__agenda = dict()
        self.__beam_size = beamSize

    def getKeySet(self) -> List[State]:
        return list(self.__agenda)

    def updateAgenda(self,
                     oracle: ScoringOracle,
                     current: State):
        if current in self.__agenda:
            return
        point = oracle.score(current)
        if len(self.__agenda) < self.__beam_size:
            self.__agenda[current] = point
        else:
            worst = None
            worst_value = sys.maxsize
            for key in self.__agenda:
                if self.__agenda[key] < worst_value:
                    worst_value = self.__agenda[key]
                    worst = key
            if point > worst_value:
                self.__agenda.pop(worst)
                self.__agenda[current] = point

    def best(self) -> State:
        best = None
        best_value = sys.maxsize
        for key in self.__agenda:
            if self.__agenda[key] > best_value:
                best_value = self.__agenda[key]
                best = key
        return best
