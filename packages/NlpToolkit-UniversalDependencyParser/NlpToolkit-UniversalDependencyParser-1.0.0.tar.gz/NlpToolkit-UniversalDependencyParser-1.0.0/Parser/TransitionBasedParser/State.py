from typing import List

from DependencyParser.Universal.UniversalDependencyRelation import UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyTreeBankWord import UniversalDependencyTreeBankWord
from DependencyParser.Universal.UniversalDependencyType import UniversalDependencyType

from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.StackRelation import StackRelation
from Parser.TransitionBasedParser.StackWord import StackWord
from Parser.TransitionBasedParser.TransitionSystem import TransitionSystem


class State:

    __stack: List[StackWord]
    __word_list: List[StackWord]
    __relations: List[StackRelation]

    def __init__(self,
                 stack: list,
                 wordList: list,
                 relations: list):
        self.__stack = stack
        self.__word_list = wordList
        self.__relations = relations

    def applyShift(self):
        if len(self.__word_list) > 0:
            self.__stack.append(self.__word_list.pop(0))

    def applyLeftArc(self, _type: UniversalDependencyType):
        if len(self.__stack) > 1:
            before_last = self.__stack[len(self.__stack) - 2].getWord()
            index = self.__stack[len(self.__stack) - 1].getToWord()
            before_last.setRelation(UniversalDependencyRelation(index, _type.name.replace("_", ":")))
            self.__stack.pop(len(self.__stack) - 2)
            self.__relations.append(StackRelation(before_last, UniversalDependencyRelation(index, _type.name.replace("_", ":"))))

    def applyRightArc(self, _type: UniversalDependencyType):
        if len(self.__stack) > 1:
            last = self.__stack[len(self.__stack) - 1].getWord()
            index = self.__word_list[0].getToWord()
            last.setRelation(UniversalDependencyRelation(index, _type.name.replace("_", ":")))
            self.__stack.pop()
            self.__relations.append(StackRelation(last, UniversalDependencyRelation(index, _type.name.replace("_", ":"))))

    def applyArcEagerLeftArc(self, _type: UniversalDependencyType):
        if len(self.__stack) > 0 and len(self.__word_list) > 0:
            last_element_of_stack = self.__stack[len(self.__stack) - 1].getWord()
            index = self.__word_list[0].getToWord()
            last_element_of_stack.setRelation(UniversalDependencyRelation(index, _type.name.replace("_", ":")))
            self.__stack.pop()
            self.__relations.append(StackRelation(last_element_of_stack, UniversalDependencyRelation(index, _type.name.replace("_", ":"))))

    def applyArcEagerRightArc(self, _type: UniversalDependencyType):
        if len(self.__stack) > 0 and len(self.__word_list) > 0:
            first_element_of_word_list = self.__word_list[0].getWord()
            index = self.__stack[len(self.__stack) - 1].getToWord()
            first_element_of_word_list.setRelation(UniversalDependencyRelation(index, _type.name.replace("_", ":")))
            self.applyShift()
            self.__relations.append(StackRelation(first_element_of_word_list, UniversalDependencyRelation(index, _type.name.replace("_", ":"))))

    def applyReduce(self):
        if len(self.__stack) > 0:
            self.__stack.pop()

    def apply(self, command: Command, _type: UniversalDependencyType, transitionSystem: TransitionSystem):
        if transitionSystem == TransitionSystem.ARC_STANDARD:
            if command == Command.LEFTARC:
                self.applyLeafArc(_type)
            elif command == Command.RIGHTARC:
                self.applyRightArc(_type)
            elif command == Command.SHIFT:
                self.applyShift()
        elif transitionSystem == TransitionSystem.ARC_EAGER:
            if command == Command.LEFTARC:
                self.applyArcEagerLeftArc(_type)
            elif command == Command.RIGHTARC:
                self.applyArcEagerRightArc(_type)
            elif command == Command.SHIFT:
                self.applyShift()
            elif command == Command.REDUCE:
                self.applyReduce()

    def relationSize(self) -> int:
        return len(self.__relations)

    def wordListSize(self) -> int:
        return len(self.__word_list)

    def stackSize(self) -> int:
        return len(self.__stack)

    def getStackWord(self, index: int) -> UniversalDependencyTreeBankWord:
        size = len(self.__stack) - 1
        if size - index < 0:
            return None
        return self.__stack[size - index].getWord()

    def getPeek(self) -> UniversalDependencyTreeBankWord:
        if len(self.__stack) > 0:
            return self.__stack[len(self.__stack) - 1].getWord()
        return None

    def getWordListWord(self, index: int) -> UniversalDependencyTreeBankWord:
        if index > len(self.__word_list) - 1:
            return None
        return self.__word_list[index].getWord()

    def getRelation(self, index: int) -> StackRelation:
        if index < len(self.__relations):
            return self.__relations[index]
        return None
