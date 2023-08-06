from random import random


cdef class RandomScoringOracle(ScoringOracle):

    cpdef float score(self, State state):
        return random.random()
