from enum import Enum


class PollStatus(Enum):
    IN_PROGRESS = 0
    CLOSED = 1


class OptionStatus(Enum):
    YES = 0
    NO = 1
    MAYBE = 2

    @staticmethod
    def values():
        return [0, 1, 2]
