"""module mode_enum. Utility enumeration
to discriminate modes when running a model

"""
import enum


class ModeEnum(enum.Enum):
    INVALID_MODE = 0
    TRAIN = 1
    TEST = 2
    VALIDATE = 3
