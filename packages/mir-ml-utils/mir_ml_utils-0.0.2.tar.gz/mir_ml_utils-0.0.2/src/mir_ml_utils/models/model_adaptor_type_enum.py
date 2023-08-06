import enum


class ModelAdaptorTypeEnum(enum.Enum):
    INVALID = 0
    LINEAR_LAYER_ADAPTOR = 1,
    FLATTEN_LAYER_ADAPTOR = 2,
    COMPOSED_ADAPTOR = 3
    NONE = 4

    @staticmethod
    def from_str(adaptor_type: str) -> enum.Enum:

        if adaptor_type == 'LINEAR_LAYER_ADAPTOR':
            return ModelAdaptorTypeEnum.LINEAR_LAYER_ADAPTOR
        elif adaptor_type == 'FLATTEN_LAYER_ADAPTOR':
            return ModelAdaptorTypeEnum.FLATTEN_LAYER_ADAPTOR
        elif adaptor_type == 'COMPOSED_ADAPTOR':
            return ModelAdaptorTypeEnum.COMPOSED_ADAPTOR
        elif adaptor_type == 'INVALID':
            return ModelAdaptorTypeEnum.INVALID
        elif adaptor_type == "NONE":
            return ModelAdaptorTypeEnum.NONE

        raise ValueError(f"adaptor_type={adaptor_type} is unknown")