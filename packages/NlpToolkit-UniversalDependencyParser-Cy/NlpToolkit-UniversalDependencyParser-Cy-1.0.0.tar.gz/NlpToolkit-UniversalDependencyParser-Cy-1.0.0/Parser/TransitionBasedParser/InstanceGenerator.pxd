from DependencyParser.Universal.UniversalDependencyTreeBankWord cimport UniversalDependencyTreeBankWord

cdef class InstanceGenerator:

    cpdef addAttributeForFeatureType(self,
                                   UniversalDependencyTreeBankWord word,
                                   list attributes,
                                   str featureType)
    cpdef addEmptyAttributes(self, list attributes)
    cpdef addFeatureAttributes(self,
                             UniversalDependencyTreeBankWord word,
                             list attributes)