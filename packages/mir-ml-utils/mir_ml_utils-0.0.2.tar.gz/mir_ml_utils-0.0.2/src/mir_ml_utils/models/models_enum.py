from enum import Enum


class ModelEnum(Enum):
    INVALID = 0
    RESNET_50 = 1
    RESNET_18 = 2
    RESNET_101 = 3
    PROTO_NET_RESNET_18 = 4
    PROTO_NET_RESNET_50 = 5

    @staticmethod
    def from_str(model: str):
        if model == "RESNET_50":
            return ModelEnum.RESNET_50
        elif model == "RESNET_18":
            return ModelEnum.RESNET_18
        elif model == "RESNET_101":
            return ModelEnum.RESNET_101
        elif model == "PROTO_NET_RESNET_18":
            return ModelEnum.PROTO_NET_RESNET_18
        elif model == "PROTO_NET_RESNET_50":
            return ModelEnum.PROTO_NET_RESNET_50

        raise ValueError("Invalid model name")
