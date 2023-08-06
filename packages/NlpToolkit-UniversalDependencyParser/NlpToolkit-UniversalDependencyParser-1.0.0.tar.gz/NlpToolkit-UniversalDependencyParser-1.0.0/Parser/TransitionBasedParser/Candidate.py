from DependencyParser.Universal.UniversalDependencyType import UniversalDependencyType

from Parser.TransitionBasedParser.Command import Command


class Candidate:

    __command: Command
    __universal_dependency_type: UniversalDependencyType

    def __init__(self,
                 command: Command,
                 universalDependencyType: UniversalDependencyType):
        self.__command = command
        self.__universal_dependency_type = universalDependencyType

    def getCommand(self) -> Command:
        return self.__command

    def getUniversalDependencyType(self) -> UniversalDependencyType:
        return self.__universal_dependency_type
