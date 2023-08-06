from DependencyParser.Universal.UniversalDependencyRelation import UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyTreeBankWord import UniversalDependencyTreeBankWord


class StackRelation:
    __word: UniversalDependencyTreeBankWord
    __relation: UniversalDependencyRelation

    def __init__(self,
                 word: UniversalDependencyTreeBankWord,
                 relation: UniversalDependencyRelation):
        self.__word = word
        self.__relation = relation

    def getWord(self) -> UniversalDependencyTreeBankWord:
        return self.__word

    def getRelation(self) -> UniversalDependencyRelation:
        return self.__relation
