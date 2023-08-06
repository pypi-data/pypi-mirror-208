from enum import Enum


class ModelTrainerTypeEnum(Enum):
    INVALID = 0
    PYTORCH_OBJECT_DETECTOR = 1
    PYTORCH_CLASSIFIER = 2
    PYTORCH_PROTOTYPICAL_CLASSIFIER = 3


VALID_TRAINERS = [ModelTrainerTypeEnum.PYTORCH_CLASSIFIER,
                  ModelTrainerTypeEnum.PYTORCH_PROTOTYPICAL_CLASSIFIER,
                  ModelTrainerTypeEnum.PYTORCH_OBJECT_DETECTOR]
