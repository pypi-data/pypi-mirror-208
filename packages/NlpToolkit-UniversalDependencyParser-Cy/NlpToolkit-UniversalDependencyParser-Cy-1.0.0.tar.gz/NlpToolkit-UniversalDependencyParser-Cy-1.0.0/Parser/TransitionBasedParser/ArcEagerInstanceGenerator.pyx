from Classification.Attribute.DiscreteIndexedAttribute cimport DiscreteIndexedAttribute
from Classification.Instance.Instance cimport Instance
from DependencyParser.Universal.UniversalDependencyTreeBankFeatures cimport UniversalDependencyTreeBankFeatures
from DependencyParser.Universal.UniversalDependencyTreeBankWord cimport UniversalDependencyTreeBankWord

cdef class ArcEagerInstanceGenerator(InstanceGenerator):

    cpdef bint suitable(self, UniversalDependencyTreeBankWord word):
        return word.getRelation() is not None

    cpdef Instance generate(self,
                            State state,
                            int windowSize,
                            str command):
        instance = Instance(command)
        attributes = []
        for i in range(windowSize):
            word = state.getStackWord(i)
            if word is None:
                attributes.append(DiscreteIndexedAttribute("null", 0, 18))
                self.addEmptyAttributes(attributes)
                attributes.append(DiscreteIndexedAttribute("null", 0, 59))
            else:
                if word.getName() == "root":
                    attributes.append(DiscreteIndexedAttribute("root", 0, 18))
                    self.addEmptyAttributes(attributes)
                    attributes.append(DiscreteIndexedAttribute("null", 0, 59))
                else:
                    attributes.append(DiscreteIndexedAttribute(word.getUpos().name, UniversalDependencyTreeBankFeatures.posIndex(word.getUpos().name) + 1, 18))
                    self.addFeatureAttributes(word, attributes)
                    if self.suitable(word):
                        attributes.append(DiscreteIndexedAttribute(word.getRelation().__str__(), UniversalDependencyTreeBankFeatures.dependencyIndex(word.getRelation().__str__()) + 1, 59))
                    else:
                        attributes.append(DiscreteIndexedAttribute("null", 0, 59))
        for i in range(windowSize):
            word = state.getWordListWord(i)
            if word is not None:
                attributes.append(DiscreteIndexedAttribute(word.getUpos().name, UniversalDependencyTreeBankFeatures.posIndex(word.getUpos().name) + 1, 18))
                self.addFeatureAttributes(word, attributes)
            else:
                attributes.append(DiscreteIndexedAttribute("root", 0, 18))
                self.addEmptyAttributes(attributes)
        for attribute in attributes:
            instance.addAttribute(attribute)
        return instance
