from abc import abstractmethod
from typing import List

from Classification.Attribute.Attribute import Attribute
from Classification.Attribute.DiscreteIndexedAttribute import DiscreteIndexedAttribute
from Classification.Instance.Instance import Instance
from DependencyParser.Universal.UniversalDependencyTreeBankFeatures import UniversalDependencyTreeBankFeatures
from DependencyParser.Universal.UniversalDependencyTreeBankWord import UniversalDependencyTreeBankWord

from Parser.TransitionBasedParser.State import State


class InstanceGenerator:

    @abstractmethod
    def generate(self,
                 state: State,
                 windowSize: int,
                 command: str) -> Instance:
        pass

    def addAttributeForFeatureType(self,
                                   word: UniversalDependencyTreeBankWord,
                                   attributes: List[Attribute],
                                   featureType: str):
        feature = word.getFeatureValue(featureType)
        number_of_values = UniversalDependencyTreeBankFeatures.numberOfValues("tr", featureType) + 1
        if feature is not None:
            attributes.append(DiscreteIndexedAttribute(feature,
                                                       UniversalDependencyTreeBankFeatures.featureValueIndex("tr", featureType, feature) + 1,
                                                       number_of_values))
        else:
            attributes.append(DiscreteIndexedAttribute("null", 0, number_of_values))

    def addEmptyAttributes(self, attributes: List[Attribute]):
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "PronType") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "NumType") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Number") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Case") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Definite") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Degree") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "VerbForm") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Mood") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Tense") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Aspect") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Voice") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Evident") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Polarity") + 1))
        attributes.append(DiscreteIndexedAttribute("null", 0, UniversalDependencyTreeBankFeatures.numberOfValues("tr", "Person") + 1))

    def addFeatureAttributes(self,
                             word: UniversalDependencyTreeBankWord,
                             attributes: List[Attribute]):
        self.addAttributeForFeatureType(word, attributes, "PronType")
        self.addAttributeForFeatureType(word, attributes, "NumType")
        self.addAttributeForFeatureType(word, attributes, "Number")
        self.addAttributeForFeatureType(word, attributes, "Case")
        self.addAttributeForFeatureType(word, attributes, "Definite")
        self.addAttributeForFeatureType(word, attributes, "Degree")
        self.addAttributeForFeatureType(word, attributes, "VerbForm")
        self.addAttributeForFeatureType(word, attributes, "Mood")
        self.addAttributeForFeatureType(word, attributes, "Tense")
        self.addAttributeForFeatureType(word, attributes, "Aspect")
        self.addAttributeForFeatureType(word, attributes, "Voice")
        self.addAttributeForFeatureType(word, attributes, "Evident")
        self.addAttributeForFeatureType(word, attributes, "Polarity")
        self.addAttributeForFeatureType(word, attributes, "Person")
