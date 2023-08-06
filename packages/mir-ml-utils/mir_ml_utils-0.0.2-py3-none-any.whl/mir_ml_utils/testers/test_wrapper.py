"""test_wrapper. Helper class to test PyTorch models

"""
import torch
import torch.nn as nn
from typing import List, Dict
from torch.utils.data import DataLoader
from loguru import logger
from pathlib import Path

from mir_ml_utils.factories.model_adaptor_factory import model_adaptor_builder
from mir_ml_utils.factories.model_builder_factory import model_loader
from mir_ml_utils.trainers.model_trainer_type_enum import ModelTrainerTypeEnum
from mir_ml_utils.models.model_adaptor_type_enum import ModelAdaptorTypeEnum
from mir_ml_utils.models.easyfsl_proto_net_classifier import EasyFSLProtoNetClassifier
from .inference_enum_types import InferenceTypeEnum


def _init_class_dict(classes: List[str]):
    class_dict = {}
    for class_name in classes:
        class_dict[class_name] = 0
    return class_dict


class TestWrapper(object):

    @staticmethod
    def print_test_classifier_info_two_classes(total_predictions: int,
                                               correct_predictions: int,
                                               incorrect_class_1_images: int,
                                               correct_class_1_images: int,
                                               incorrect_class_0_images: int,
                                               correct_class_0_images: int,
                                               class0_name: str,
                                               class1_name: str) -> Dict:

        accuracy = float(correct_predictions) / float(total_predictions)
        logger.info(f"Model accuracy {accuracy}")
        logger.info(f"Model TP (i.e {class1_name} img and model predicted it)={correct_class_1_images}")
        logger.info(f"Model TN (i.e {class0_name} img  and model predicted it)={correct_class_0_images}")
        logger.info(f"Model FP (i.e this is not {class1_name} img but model predicted it)={incorrect_class_0_images}")
        logger.info(
            f"Model FN (i.e this is  {class1_name} img  but model did not "
            f"predicted it. It predicted {class0_name})={incorrect_class_1_images}")

        tp = correct_class_1_images
        tn = correct_class_0_images
        fp = incorrect_class_0_images
        fn = incorrect_class_1_images

        recall = float(tp) / (float(tp) + float(fn))
        precision = float(tp) / (float(tp) + float(fp))
        fscore = (2 * recall * precision) / (precision + recall)

        logger.info(f"Model recall={recall}")
        logger.info(f"Model precision={precision}")
        logger.info(f"Model fscore={fscore}")
        return {"accuracy": accuracy, "recall": recall,
                "precision": precision, "Fscore": fscore,
                "details": {"tp": tp, "tn": tn, "fp": fp, "fn": fn}}

    def __init__(self, config: dict):
        self.config = config
        self.device = 'cuda:0' if torch.cuda.is_available() and self.config['train_options']['use_cuda'] else 'cpu'
        self.simulation_data_dir_output: Path = self.config['run_dir_output'] / self.config['run_name']

    def run_test_classification_model(self, model: nn.Module = None,
                                      test_dataset: DataLoader = None):

        if model is None:
            logger.warning("Model is None loading model from config file")

            model_adaptor_options = {"n_classes": self.config['train_options']['n_classes']}

            if self.config['test_options']['model_adaptor']['name'] != ModelAdaptorTypeEnum.NONE:
                model_adaptor_options.update(self.config['test_options']['model_adaptor']["properties"])

            model_adaptor = model_adaptor_builder(
                adaptor_type=self.config['test_options']['model_adaptor']['name'],
                options=model_adaptor_options)
            model = model_loader(builder_name=self.config['train_options']['model_builder_factory'],
                                 config={'model_type': self.config['train_options']['model_type'],
                                         'model_path': self.simulation_data_dir_output / self.config['best_model_name'],
                                         'model_adaptor': model_adaptor,
                                         'device': self.device,
                                         'with_pretrained': self.config['train_options']['with_pretrained'],
                                         'freeze_model_parameters': self.config['train_options'][
                                             'freeze_model_parameters']})

        # set the model to eval mode so that no
        # gradient claculation is performed
        model.eval()

        # check the type of the classifier and
        # act analogously

        if self.config["train_options"]["trainer_type"] == ModelTrainerTypeEnum.PYTORCH_PROTOTYPICAL_CLASSIFIER:
            return self._test_prototypical_network(model=model, dataloader=test_dataset)
        else:
            raise ValueError(f" Invalid model type={self.config['training_options']['trainer_type'].name}")

    def run_test_object_detection_model(self, model: nn.Module = None,
                                        test_dataset: DataLoader = None,
                                        masks_dataset=None):
        pass

    def _test_prototypical_network(self, model: EasyFSLProtoNetClassifier, dataloader: DataLoader):

        if self.config['test_options']['inference_with'] == InferenceTypeEnum.WITH_PROTOTYPES:
            # a few shot classifier based in prototypical networks requires
            # new the prototypes in order to be tested
            prototypes_filenames = self.simulation_data_dir_output / self.config['test_options']['few_shot_options'][
                'prototypes_filenames']
            logger.info(f"Loading prototypes from {prototypes_filenames}")
            prototypes = torch.load(prototypes_filenames,
                                    map_location=torch.device(self.device))

            logger.info(f"Testing with prototypes")
            logger.info(f"Prototypes size {prototypes.size()}")
            model.set_prototypes(prototypes=prototypes)

            best_prototypes, test_accuracy, batch_monitors = EasyFSLProtoNetClassifier.do_test_prototypical_network(
                model=model,
                dataloader=dataloader,
                classes=list(self.config["classes"].values()))

            for item in batch_monitors:
                logger.info(f"Test monitor: {item}={batch_monitors[item]}")

            return best_prototypes, test_accuracy, batch_monitors
        elif self.config['test_options']['inference_with'] == InferenceTypeEnum.USUAL_TESTING:
            return EasyFSLProtoNetClassifier.do_test_prototypical_network(model=model,
                                                                          dataloader=dataloader,
                                                                          classes=list(self.config["classes"].values()))
        else:
            raise ValueError(f"Invalid set up for testing {self.config['test_options']['inference_with']}")

    """
        elif options['few_shot_inference_with'] == 'usual_testing':
            logger.info(f"Using usual testing")
            logger.info(f"Loading prototypes from {options['few_shot_prototypes_file_path']}")
            prototypes = torch.load(options['few_shot_prototypes_file_path'],
                                    map_location=torch.device(device))

            model.set_prototypes(prototypes=prototypes)
            out = TwoClassPyTorchModelTester.evaluate_on_dataloader(model=model,
                                                                dataloader=dataloader,
                                                                device=device,
                                                                class0_name=class0_name,
                                                                class1_name=class1_name)
            best_prototypes = prototypes

        else:
            logger.info(f"Testing without prototypes")
            out, best_prototypes = do_test_model(prototypes=None, model=model, dataloader=dataloader)

    return out, best_prototypes
    """
