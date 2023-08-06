import copy
from typing import List

from Classification.Instance.Instance import Instance
from DependencyParser.Universal.UniversalDependencyTreeBankSentence import UniversalDependencyTreeBankSentence
from DependencyParser.Universal.UniversalDependencyTreeBankWord import UniversalDependencyTreeBankWord

from Parser.TransitionBasedParser.ArcEagerInstanceGenerator import ArcEagerInstanceGenerator
from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.Oracle import Oracle
from Parser.TransitionBasedParser.StackWord import StackWord
from Parser.TransitionBasedParser.State import State
from Parser.TransitionBasedParser.TransitionParser import TransitionParser


class ArcEagerTransitionParser(TransitionParser):

    def __init__(self):
        super().__init__()

    def simulateParse(self,
                      sentence: UniversalDependencyTreeBankSentence,
                      windowSize: int) -> List[Instance]:
        top_relation = None
        instance_generator = ArcEagerInstanceGenerator()
        instance_list = []
        word_map = dict()
        word_list = []
        stack = []
        for j in range(sentence.wordCount()):
            word = sentence.getWord(j)
            if isinstance(word, UniversalDependencyTreeBankWord):
                clone = copy.deepcopy(word)
                clone.setRelation(None)
                word_map[j + 1] = word
                word_list.append(StackWord(clone, j + 1))
        stack.append(StackWord())
        state = State(stack, word_list, [])
        while len(word_list) > 0 or len(stack) > 1:
            if len(word_list) != 0:
                first = word_list[0].getWord()
                first_relation = word_map[word_list[0].getToWord()].getRelation()
            else:
                first = None
                first_relation = None
            top = stack[len(stack) - 1].getWord()
            if top.getName() != "root":
                top_relation = word_map[stack[len(stack) - 1].getToWord()].getRelation()
            if len(stack) > 1:
                if first_relation is not None and first_relation.to() == top.getId():
                    instance_list.append(
                        instance_generator.generate(state, windowSize, "RIGHTARC(" + first_relation.__str__() + ")"))
                    word = word_list.pop(0)
                    stack.append(StackWord(word_map[word.getToWord()], word.getToWord()))
                elif first is not None and top_relation is not None and top_relation.to() == first.getId():
                    instance_list.append(
                        instance_generator.generate(state, windowSize, "LEFTARC(" + top_relation.__str__() + ")"))
                    stack.pop()
                elif len(word_list) > 0:
                    instance_list.append(instance_generator.generate(state, windowSize, "SHIFT"))
                    stack.append(word_list.pop(0))
                else:
                    instance_list.append(instance_generator.generate(state, windowSize, "REDUCE"))
                    stack.pop()
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
                state.applyArcEagerLeftArc(decision.getUniversalDependencyType())
            elif decision.getCommand() == Command.RIGHTARC:
                state.applyArcEagerRightArc(decision.getUniversalDependencyType())
            elif decision.getCommand() == Command.REDUCE:
                state.applyReduce()
        return sentence
