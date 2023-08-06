from pathlib import Path
from typing import Any, Callable, Union
import torch
import torch.nn as nn
from torchvision import models
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from loguru import logger

from .models_enum import ModelEnum
from .easyfsl_proto_net_classifier import EasyFSLProtoNetClassifier


class ResNetModelLoader(object):

    @staticmethod
    def build_from_config(config: dict):
        return ResNetModelLoader.build(model_type=config['model_type'],
                                       device=config['device'],
                                       pretrained=config['with_pretrained'],
                                       model_adaptor=config['model_adaptor'],
                                       freeze_model_params=config['freeze_model_parameters'],
                                       weights=config['weights'] if 'weights' in config else None)

    @staticmethod
    def load_from_config(config: dict):
        return ResNetModelLoader.load(model_type=config['model_type'],
                                      model_path=config['model_path'],
                                      model_adaptor=config['model_adaptor'],
                                      device=config['device'],
                                      freeze_model_params=config['freeze_model_parameters'],
                                      pretrained=config['with_pretrained'],
                                      weights=config['weights'] if 'weights' in config else None)

    @staticmethod
    def build(model_type: Union[ModelEnum | str], device: str = 'cpu',
              pretrained: bool = True, weights: Any = None,
              model_adaptor: Callable = None,
              freeze_model_params: bool = True) -> nn.Module:

        if isinstance(model_type, str):
            model_type = ModelEnum.from_str(model=model_type)

        if model_type == ModelEnum.RESNET_18:

            if pretrained and weights is None:
                model_ft = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            elif pretrained and weights is not None:
                model_ft = models.resnet18(weights=weights)
            else:
                model_ft = models.resnet18(weights=None)
        elif model_type == ModelEnum.RESNET_50:
            if pretrained and weights is None:
                model_ft = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            elif pretrained and weights is not None:
                model_ft = models.resnet50(weights=weights)
            else:
                model_ft = models.resnet50(weights=None)
        elif model_type == ModelEnum.RESNET_101:
            if pretrained and weights is None:
                model_ft = models.resnet101(weights=models.ResNet101_Weights.DEFAULT)
            elif pretrained and weights is not None:
                model_ft = models.resnet101(weights=weights)
            else:
                model_ft = models.resnet101(weights=None)
        else:
            raise ValueError(f"Model type {model_type} not in [RESNET_18, RESNET_50, RESNET_101]")

        if freeze_model_params:
            for param in model_ft.parameters():
                param.requires_grad = False

        if model_adaptor is not None:
            model_ft = model_adaptor(model_ft)

        model_ft.to(device=device)
        return model_ft

    @staticmethod
    def load(model_type: ModelEnum,
             model_path: Path,
             model_adaptor: Callable = None,
             device: str = 'cpu',
             freeze_model_params: bool = True,
             pretrained: bool = True, weights: Any = None) -> nn.Module:

        model_ft = ResNetModelLoader.build(model_type=model_type,
                                           model_adaptor=model_adaptor,
                                           device=device,
                                           freeze_model_params=freeze_model_params,
                                           pretrained=pretrained,
                                           weights=weights)

        model_ft.load_state_dict(torch.load(model_path, map_location=torch.device(device)))
        return model_ft


class ProtoNetModelLoader(object):

    @staticmethod
    def build_from_config(config: dict):

        if config['model_type'] == ModelEnum.PROTO_NET_RESNET_50:
            backbone_net = ModelEnum.RESNET_50
        elif config['model_type'] == ModelEnum.PROTO_NET_RESNET_18:
            backbone_net = ModelEnum.RESNET_18
        else:
            raise ValueError(f"Model type {config['model_type']} not in "
                             f"['PROTO_NET_RESNET_18', 'PROTO_NET_RESNET_50']")

        logger.info(f"Backbone net is set to {backbone_net} ")
        logger.info(f"Model is set to {config['device']} ")
        convolutional_network = ResNetModelLoader.build(model_type=backbone_net,
                                                        device=config['device'],
                                                        pretrained=config['with_pretrained'],
                                                        model_adaptor=config['model_adaptor'],
                                                        freeze_model_params=config['freeze_model_parameters'],
                                                        weights=config['weights'] if 'weights' in config else None)

        model = EasyFSLProtoNetClassifier(backbone=convolutional_network,
                                          model_name=config['model_type'],
                                          device=config['device'])

        model.to(device=config['device'])
        return model

    @staticmethod
    def load_from_config(config: dict):

        if config['model_type'] == ModelEnum.PROTO_NET_RESNET_50:
            backbone_net = ModelEnum.from_str("RESNET_50")
        elif config['model_type'] == ModelEnum.PROTO_NET_RESNET_18:
            backbone_net = ModelEnum.from_str("RESNET_18")
        else:
            raise ValueError(f"Model type {config['model_type']} not in "
                             f"['PROTO_NET_RESNET_18', 'PROTO_NET_RESNET_50']")

        logger.info(f"Backbone net is set to {backbone_net} ")
        logger.info(f"Model is set to {config['device']} ")
        convolutional_network = ResNetModelLoader.build(model_type=backbone_net,
                                                        device=config['device'],
                                                        pretrained=config['with_pretrained'],
                                                        model_adaptor=config['model_adaptor'],
                                                        freeze_model_params=config['freeze_model_parameters'],
                                                        weights=config['weights'] if 'weights' in config else None)

        model = EasyFSLProtoNetClassifier(backbone=convolutional_network,
                                          model_name=config['model_type'],
                                          device=config['device'])

        model.load_state_dict(torch.load(config['model_path'],
                                         map_location=torch.device(config['device'])))
        model.to(device=config['device'])

        return model

    @staticmethod
    def build(model_type: Union[ModelEnum | str], device: str = 'cpu',
              pretrained: bool = True, weights: Any = None,
              model_adaptor: Callable = None,
              freeze_model_params: bool = True) -> nn.Module:

        raise NotImplementedError("Function not implemented")

    @staticmethod
    def load(model_type: ModelEnum,
             model_path: Path,
             model_adaptor: Callable = None,
             device: str = 'cpu',
             freeze_model_params: bool = True,
             pretrained: bool = True, weights: Any = None) -> nn.Module:

        raise NotImplementedError("Function not implemented")


class MaskRCNNModelLoader(object):

    @staticmethod
    def build_from_config(config: dict):

        if config['model_type'] == "MASK_RCNN_RESNET_50":

            if config['with_pretrained']:
                # check this: https://www.kaggle.com/code/tungxnguyen/corrosion-mask-rcnn/notebook
                # Kaggle notebook how to build the model
                # load an instance segmentation model pre-trained on COCO
                # check this link
                # https://pytorch.org/vision/main/models/generated/torchvision.models.detection.maskrcnn_resnet50_fpn_v2.html#torchvision.models.detection.MaskRCNN_ResNet50_FPN_V2_Weights
                # this is equivalent to COCO_V1

                if 'weights' not in config or config['weights'] is None:

                    model = models.detection.maskrcnn_resnet50_fpn(weights=models.detection.MaskRCNN_ResNet50_FPN_Weights.DEFAULT)
                else:
                    model = models.detection.maskrcnn_resnet50_fpn(weights=config['weights'])

                # get the number of input features for the classifier
                in_features = model.roi_heads.box_predictor.cls_score.in_features

                # replace the pre-trained head with a new one
                model.roi_heads.box_predictor = FastRCNNPredictor(in_features, config['n_classes'])

                # now get the number of input features for the mask classifier
                in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
                hidden_layer = 256

                # and replace the mask predictor with a new one
                model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask,
                                                                   hidden_layer,
                                                                   config['n_classes'])

                model.to(device=config['device'])
                return model
        else:
            raise ValueError(f"Model type {config['model_type']} not in "
                             f"['MASK_RCNN_RESNET_50']")

    @staticmethod
    def load_from_config(config: dict):
        model = MaskRCNNModelLoader.build_from_config(config=config)
        model.load_state_dict(torch.load(config['model_path'],
                                         map_location=torch.device(config['device'])))
        model.to(device=config['device'])
        return model

