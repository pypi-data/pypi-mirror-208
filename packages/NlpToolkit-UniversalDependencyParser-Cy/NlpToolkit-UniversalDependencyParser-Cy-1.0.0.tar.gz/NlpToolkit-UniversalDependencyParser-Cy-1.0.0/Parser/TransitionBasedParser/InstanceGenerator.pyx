from abc import abstractmethod

from Classification.Attribute.DiscreteIndexedAttribute cimport DiscreteIndexedAttribute
from Classification.Instance.Instance cimport Instance
from DependencyParser.Universal.UniversalDependencyTreeBankFeatures cimport UniversalDependencyTreeBankFeatures
from DependencyParser.Universal.UniversalDependencyTreeBankWord cimport UniversalDependencyTreeBankWord

from Parser.TransitionBasedParser.State cimport State

cdef class InstanceGenerator:

    @abstractmethod
    def generate(self,
                 state: State,
                 windowSize: int,
                 command: str) -> Instance:
        pass

    cpdef addAttributeForFeatureType(self,
                                     UniversalDependencyTreeBankWord word,
                                     list attributes,
                                     str featureType):
        feature = word.getFeatureValue(featureType)
        number_of_values = UniversalDependencyTreeBankFeatures.numberOfValues("tr", featureType) + 1
        if feature is not None:
            attributes.append(DiscreteIndexedAttribute(feature,
                                                       UniversalDependencyTreeBankFeatures.featureValueIndex("tr", featureType, feature) + 1,
                                                       number_of_values))
        else:
            attributes.append(DiscreteIndexedAttribute("null", 0, number_of_values))

    cpdef addEmptyAttributes(self, list attributes):
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

    cpdef addFeatureAttributes(self,
                               UniversalDependencyTreeBankWord word,
                               list attributes):
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
