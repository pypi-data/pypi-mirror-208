import sys

cdef class Agenda:

    def __init__(self, beamSize: int):
        self.__agenda = dict()
        self.__beam_size = beamSize

    cpdef list getKeySet(self):
        return list(self.__agenda)

    cpdef updateAgenda(self,
                       ScoringOracle oracle,
                       State current):
        if current in self.__agenda:
            return
        point = oracle.score(current)
        if len(self.__agenda) < self.__beam_size:
            self.__agenda[current] = point
        else:
            worst = None
            worst_value = sys.maxsize
            for key in self.__agenda:
                if self.__agenda[key] < worst_value:
                    worst_value = self.__agenda[key]
                    worst = key
            if point > worst_value:
                self.__agenda.pop(worst)
                self.__agenda[current] = point

    cpdef State best(self):
        best = None
        best_value = sys.maxsize
        for key in self.__agenda:
            if self.__agenda[key] > best_value:
                best_value = self.__agenda[key]
                best = key
        return best
