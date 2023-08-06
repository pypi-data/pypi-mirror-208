from DependencyParser.Universal.UniversalDependencyTreeBankWord import UniversalDependencyTreeBankWord


class StackWord:

    __word: UniversalDependencyTreeBankWord
    __to_word: int

    def constructor1(self):
        self.__word = UniversalDependencyTreeBankWord()
        self.__to_word = 0

    def constructor2(self, word: UniversalDependencyTreeBankWord, toWord: int):
        self.__word = word
        self.__to_word = toWord

    def __init__(self,
                 word: UniversalDependencyTreeBankWord = None,
                 toWord: int = None):
        if word is None:
            self.constructor1()
        else:
            self.constructor2(word, toWord)

    def getWord(self) -> UniversalDependencyTreeBankWord:
        return self.__word

    def getToWord(self) -> int:
        return self.__to_word
