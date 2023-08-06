from enum import Enum, auto


class TransitionSystem(Enum):

    ARC_STANDARD = auto(0)
    ARC_EAGER = auto(1)
