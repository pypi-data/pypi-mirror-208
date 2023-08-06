import copy
from abc import abstractmethod
from typing import List

from Classification.DataSet.DataSet import DataSet
from Classification.Instance.Instance import Instance
from DependencyParser.Universal.UniversalDependencyRelation import UniversalDependencyRelation
from DependencyParser.Universal.UniversalDependencyTreeBankCorpus import UniversalDependencyTreeBankCorpus
from DependencyParser.Universal.UniversalDependencyTreeBankSentence import UniversalDependencyTreeBankSentence
from DependencyParser.Universal.UniversalDependencyTreeBankWord import UniversalDependencyTreeBankWord
from DependencyParser.Universal.UniversalDependencyType import UniversalDependencyType

from Parser.TransitionBasedParser.Agenda import Agenda
from Parser.TransitionBasedParser.Candidate import Candidate
from Parser.TransitionBasedParser.Command import Command
from Parser.TransitionBasedParser.Oracle import Oracle
from Parser.TransitionBasedParser.ScoringOracle import ScoringOracle
from Parser.TransitionBasedParser.StackWord import StackWord
from Parser.TransitionBasedParser.State import State
from Parser.TransitionBasedParser.TransitionSystem import TransitionSystem


class TransitionParser:

    def __init__(self):
        pass

    def createResultSentence(self,
                             universalDependencyTreeBankSentence: UniversalDependencyTreeBankSentence) -> UniversalDependencyTreeBankSentence:
        sentence = UniversalDependencyTreeBankSentence("u")
        for i in range(universalDependencyTreeBankSentence.wordCount()):
            word = universalDependencyTreeBankSentence.getWord(i)
            if isinstance(word, UniversalDependencyTreeBankWord):
                sentence.addWord(UniversalDependencyTreeBankWord(word.getId(),
                                                                 word.getName(),
                                                                 word.getLemma(),
                                                                 word.getUpos(),
                                                                 word.getXPos(),
                                                                 word.getFeatures(),
                                                                 None,
                                                                 word.getDeps(),
                                                                 word.getMisc()))
        return sentence

    @abstractmethod
    def simulateParse(self,
                      sentence: UniversalDependencyTreeBankSentence,
                      windowSize: int) -> List[Instance]:
        pass

    @abstractmethod
    def dependencyParse(self,
                        universalDependencyTreeBankSentence: UniversalDependencyTreeBankSentence,
                        oracle: Oracle) -> UniversalDependencyTreeBankSentence:
        pass

    def simulateParseOnCorpus(self,
                              corpus: UniversalDependencyTreeBankCorpus,
                              windowSize: int):
        dataSet = DataSet()
        for i in range(corpus.sentenceCount()):
            sentence = corpus.getSentence(i)
            if isinstance(sentence, UniversalDependencyTreeBankSentence):
                dataSet.addInstanceList(self.simulateParse(sentence, windowSize))

    def checkStates(self, agenda: Agenda) -> bool:
        for state in agenda.getKeySet():
            if state.wordListSize() > 0 or state.stackSize() > 1:
                return True
        return False

    def initialState(self, sentence: UniversalDependencyTreeBankSentence) -> State:
        wordList = []
        for i in range(sentence.wordCount()):
            word = sentence.getWord(i)
            if isinstance(word, UniversalDependencyTreeBankWord):
                wordList.append(StackWord(word, i + 1))
        stack = [StackWord()]
        return State(stack, wordList, [])

    def constructCandidates(self,
                            transitionSystem: TransitionSystem,
                            state: State) -> List[Candidate]:
        if state.stackSize() == 1 and state.wordListSize() == 0:
            return []
        subsets = []
        if state.wordListSize() > 0:
            subsets.append(Candidate(Command.SHIFT, UniversalDependencyType.DEP))
        if transitionSystem == TransitionSystem.ARC_EAGER and state.stackSize() > 0:
            subsets.append(Candidate(Command.REDUCE, UniversalDependencyType.DEP))
        for i in range(len(UniversalDependencyRelation.universal_dependency_types)):
            _type = UniversalDependencyRelation.getDependencyTag(UniversalDependencyRelation.universal_dependency_types[i])
            if transitionSystem == TransitionSystem.ARC_STANDARD and state.stackSize() > 1:
                subsets.append(Candidate(Command.LEFTARC, _type))
                subsets.append(Candidate(Command.RIGHTARC, _type))
            elif transitionSystem == TransitionSystem.ARC_EAGER and state.stackSize() > 0 and state.wordListSize() > 0:
                subsets.append(Candidate(Command.LEFTARC, _type))
                subsets.append(Candidate(Command.RIGHTARC, _type))
        return subsets

    def dependencyParseWithBeamSearch(self,
                                      oracle: ScoringOracle,
                                      beamSize: int,
                                      universalDependencyTreeBankSentence: UniversalDependencyTreeBankSentence,
                                      transitionSystem: TransitionSystem) -> State:
        sentence = self.createResultSentence(universalDependencyTreeBankSentence)
        initialState = self.initialState(sentence)
        agenda = Agenda(beamSize)
        agenda.updateAgenda(oracle, copy.deepcopy(initialState))
        while self.checkStates(agenda):
            for state in agenda.getKeySet():
                subsets = self.constructCandidates(transitionSystem, state)
                for subset in subsets:
                    command = subset.getCommand()
                    _type = subset.getUniversalDependencyType()
                    cloneState = copy.deepcopy(state)
                    cloneState.apply(command, _type, transitionSystem)
                    agenda.updateAgenda(oracle, copy.deepcopy(cloneState))
        return agenda.best()

    def dependencyParseCorpus(self,
                              universalDependencyTreeBankCorpus: UniversalDependencyTreeBankCorpus,
                              oracle: Oracle) -> UniversalDependencyTreeBankCorpus:
        corpus = UniversalDependencyTreeBankCorpus()
        for i in range(universalDependencyTreeBankCorpus.sentenceCount()):
            sentence = universalDependencyTreeBankCorpus.getSentence(i)
            if isinstance(sentence, UniversalDependencyTreeBankSentence):
                corpus.addSentence(self.dependencyParse(sentence, oracle))
        return corpus
