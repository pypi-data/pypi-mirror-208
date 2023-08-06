from enum import Enum
from typing import Union
import torch.nn as nn
from mir_ml_utils.models.model_loaders import ResNetModelLoader, ProtoNetModelLoader, MaskRCNNModelLoader

VALID_MODEL_BUILDERS = ['ResNet', 'ProtoNet', 'MaskRCNN']


class ModelBuilderEnum(Enum):
    INVALID = 0
    ResNet = 1
    ProtoNet = 2
    MaskRCNN = 3

    @staticmethod
    def from_str(model: str):
        if model == "ResNet":
            return ModelBuilderEnum.ResNet
        elif model == "ProtoNet":
            return ModelBuilderEnum.ProtoNet
        elif model == "MaskRCNN":
            return ModelBuilderEnum.MaskRCNN
        raise ValueError("Invalid model name")


def model_builder(builder_name: Union[str, ModelBuilderEnum],
                  config: dict) -> nn.Module:

    if isinstance(builder_name, str):
        builder_name = ModelBuilderEnum.from_str(builder_name)

    if builder_name == ModelBuilderEnum.ResNet:
        return ResNetModelLoader.build_from_config(config=config)
    elif builder_name == ModelBuilderEnum.ProtoNet:
        return ProtoNetModelLoader.build_from_config(config=config)
    elif builder_name == ModelBuilderEnum.MaskRCNN:
        return MaskRCNNModelLoader.build_from_config(config=config)

    raise ValueError(f'Model builder={builder_name} not in {VALID_MODEL_BUILDERS}')


def model_loader(builder_name: str, config: dict) -> nn.Module:

    if builder_name == ModelBuilderEnum.ResNet:
        return ResNetModelLoader.load_from_config(config=config)
    elif builder_name == ModelBuilderEnum.ProtoNet:
        return ProtoNetModelLoader.load_from_config(config=config)

    raise ValueError(f'Model builder={builder_name} not in {VALID_MODEL_BUILDERS}')


