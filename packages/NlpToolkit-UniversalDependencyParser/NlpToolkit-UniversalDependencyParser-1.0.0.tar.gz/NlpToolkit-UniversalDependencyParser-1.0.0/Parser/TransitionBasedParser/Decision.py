from DependencyParser.Universal.UniversalDependencyType import UniversalDependencyType

from Parser.TransitionBasedParser.Candidate import Candidate
from Parser.TransitionBasedParser.Command import Command


class Decision(Candidate):

    __point: float

    def __init__(self,
                 command: Command,
                 relation: UniversalDependencyType,
                 point: float):
        super().__init__(command, relation)
        self.__point = point

    def getPoint(self) -> float:
        return self.__point
