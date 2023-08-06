from typing import List

from Classification.Instance.Instance import Instance
from DependencyParser.Universal.UniversalDependencyTreeBankSentence import UniversalDependencyTreeBankSentence
from DependencyParser.Universal.UniversalDependencyTreeBankWord import UniversalDependencyTreeBankWord

from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.Oracle import Oracle
from Parser.TransitionBasedParser.SimpleInstanceGenerator import SimpleInstanceGenerator
from Parser.TransitionBasedParser.StackWord import StackWord
from Parser.TransitionBasedParser.State import State
from Parser.TransitionBasedParser.TransitionParser import TransitionParser


class ArcStandardTransitionParser(TransitionParser):

    def __init__(self):
        super().__init__()

    def checkForMoreRelation(self,
                             wordList: List[StackWord],
                             _id: int) -> bool:
        for word in wordList:
            if word.getWord().getRelation().to() == _id:
                return False
        return True

    def simulateParse(self,
                      sentence: UniversalDependencyTreeBankSentence,
                      windowSize: int) -> List[Instance]:
        instance_generator = SimpleInstanceGenerator()
        instance_list = []
        word_list = []
        stack = []
        for j in range(sentence.wordCount()):
            word = sentence.getWord(j)
            if isinstance(word, UniversalDependencyTreeBankWord):
                word_list.append(StackWord(word, j + 1))
        stack.append(StackWord())
        state = State(stack, word_list, [])
        if len(word_list) > 0:
            instance_list.append(instance_generator.generate(state, windowSize, "SHIFT"))
            stack.append(word_list.pop(0))
            if len(word_list) > 1:
                instance_list.append(instance_generator.generate(state, windowSize, "SHIFT"))
                stack.append(word_list.pop(0))
            while len(word_list) > 0 or len(stack) > 1:
                top = stack[len(stack) - 1].getWord()
                top_relation = top.getRelation()
                if len(stack) > 1:
                    before_top = stack[len(stack) - 2].getWord()
                    before_top_relation = before_top.getRelation()
                    if before_top.getId() == top_relation.to() and self.checkForMoreRelation(word_list, top.getId()):
                        instance_list.append(instance_generator.generate(state, windowSize, "RIGHTARC(" + top_relation.__str__() + ")"))
                        stack.pop()
                    elif top.getId() == before_top_relation.to():
                        instance_list.append(instance_generator.generate(state, windowSize, "LEFTARC(" + before_top_relation.__str__() + ")"))
                        stack.pop(len(stack) - 2)
                    else:
                        if len(word_list) > 0:
                            instance_list.append(instance_generator.generate(state, windowSize, "SHIFT"))
                            stack.append(word_list.pop(0))
                        else:
                            break
                else:
                    if len(word_list) > 0:
                        instance_list.append(instance_generator.generate(state, windowSize, "SHIFT"))
                        stack.append(word_list.pop(0))
                    else:
                        break
        return instance_list

    def dependencyParse(self,
                        universalDependencyTreeBankSentence: UniversalDependencyTreeBankSentence,
                        oracle: Oracle) -> UniversalDependencyTreeBankSentence:
        sentence = self.createResultSentence(universalDependencyTreeBankSentence)
        state = self.initialState(sentence)
        while state.wordListSize() > 0 or state.stackSize() > 1:
            decision = oracle.makeDecision(state)
            if decision.getCommand() == Command.SHIFT:
                state.applyShift()
            elif decision.getCommand() == Command.LEFTARC:
                state.applyLeftArc(decision.getUniversalDependencyType())
            elif decision.getCommand() == Command.RIGHTARC:
                state.applyRightArc(decision.getUniversalDependencyType())
        return sentence
