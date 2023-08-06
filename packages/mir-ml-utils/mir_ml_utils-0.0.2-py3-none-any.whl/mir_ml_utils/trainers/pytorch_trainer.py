"""module pytorch_trainer. Specifies a trainer
for pytorch models. A PyTorchTrainer wraps three main
elements

- A model to train
- A loss model
- An optimizer
- A train & validate datasets set

"""
import copy
import numpy as np
from typing import Callable, List, Union
from dataclasses import dataclass
from pathlib import Path
from loguru import logger
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

import mir_ml_utils.mir_vision.references.detection.utils as mir_vision_utils
from mir_ml_utils.mir_vision.references.detection.coco_eval import CocoEvaluator
from mir_ml_utils.mir_vision.references.detection.engine import train_one_epoch, evaluate
from mir_ml_utils.config import PYTORCH_MODEL_FILE_EXTENSION
from mir_ml_utils.trainers.trainer_info import TrainInfo
from mir_ml_utils.utils.function_wrappers import time_func_wrapper
from mir_ml_utils.loss_functions.loss_function_result import LossFuncResult
from mir_ml_utils.trainers.model_trainer_type_enum import ModelTrainerTypeEnum, VALID_TRAINERS


@dataclass(init=True, repr=True)
class PyTorchTrainerConfig(object):
    optimizer: optim.Optimizer = None
    lr_scheduler: optim.lr_scheduler.StepLR = None
    model: nn.Module = None
    loss_func: Callable = None
    loss_func_validate: Callable = None
    n_epochs: int = 1
    device: str = 'cpu'
    log_frequency: int = 10
    model_registry_path: Path = None
    save_best_model: bool = False
    best_model_path: Path = None
    clear_cuda_cache_on_validation: bool = True
    model_name: str = None
    application_train_fit: Callable = None
    application_validation_fit: Callable = None
    best_accuracy_prototypes_filepath: Path = None
    save_model_prototypes_on_validation: bool = False
    trainer_type: ModelTrainerTypeEnum = ModelTrainerTypeEnum.INVALID


def _validate_config(config: PyTorchTrainerConfig) -> None:
    """Validate the configuration

   Parameters
   ----------
   config: The configuration object to validate

   Returns
   -------
    None
   """

    if config is None:
        raise ValueError("Configuration object is None")

    if config.model is None:
        raise ValueError("Model is not None")

    if config.optimizer is None:
        raise ValueError("Optimizer is None")

    if config.loss_func is None:
        raise ValueError("Loss function is None")

    if config.n_epochs <= 0:
        raise ValueError("Invalid number of epochs. n_epochs should be >=1")

    if config.trainer_type not in VALID_TRAINERS:
        raise ValueError(f"Trainer type {config.trainer_type} not in {VALID_TRAINERS}")

    if config.trainer_type == ModelTrainerTypeEnum.PYTORCH_PROTOTYPICAL_CLASSIFIER and config.application_train_fit is None:
        raise ValueError("Training a prototypical classifier requires to specify an application_train_fit function")

    if config.trainer_type == ModelTrainerTypeEnum.PYTORCH_PROTOTYPICAL_CLASSIFIER and config.application_validation_fit is None:
        raise ValueError(
            "Training a prototypical classifier requires to specify an application_validation_fit function")


class PyTorchTrainer(object):

    def __init__(self, config):

        _validate_config(config=config)
        self.config: PyTorchTrainerConfig = config
        self.train_loss = []
        self.train_acc = []
        self.val_loss = []
        self.val_acc = []

    def fit(self, train_data: DataLoader,
            validate_data: DataLoader, **kwargs) -> Union[TrainInfo | mir_vision_utils.MetricLogger]:
        """Fit the model on the given datasets

        Parameters
        ----------
        train_data: The train data to fit the model against
        validate_data: The  data to validate the model against

        Returns
        -------

        An instance of TrainInfo class
        """

        self.actions_before_train(train_data, validate_data)
        logger.info("Start training")
        info, total_time = self._do_train(train_data, validate_data, **kwargs)
        logger.info("Training finished. Total time={total_time}.")

        # update total training time
        info.total_time = total_time

        self.actions_after_train()
        return info

    def actions_before_train(self, train_data: DataLoader,
                             validate_data: DataLoader) -> None:
        """Handles actions before the start of training

        Returns
        -------

        """

        if train_data is None:
            raise ValueError("train_data is None")

        if self.config.save_best_model and self.config.best_model_path is None:
            raise ValueError("Invalid Configuration, save_best_model is True but best_model_path is None")

        if validate_data is not None and self.config.loss_func_validate is None:
            raise ValueError("Requested validation but the validation loss function is None")

    def actions_after_train(self) -> None:
        """Actions taken after training

        Returns
        -------

        """
        if self.config.model_registry_path is not None:
            # save the model on the given path
            # it assumes that directory is created
            # by the application

            if self.config.model_name is not None:
                file_name_extension = str(self.config.model_name) + PYTORCH_MODEL_FILE_EXTENSION
            else:
                file_name_extension = str(self.config.model.name) + PYTORCH_MODEL_FILE_EXTENSION
            file_name = self.config.model_registry_path / file_name_extension
            torch.save(self.config.model.state_dict(), file_name)

    @time_func_wrapper(show_time=True)
    def _do_train(self, train_data: DataLoader,
                  validate_data: DataLoader, **kwargs) -> Union[TrainInfo | mir_vision_utils.MetricLogger]:

        executed_epochs = 0
        best_acc = 0
        best_state = copy.deepcopy(self.config.model.state_dict())

        train_loss_result: LossFuncResult = None

        metric_logger = None
        # loop over the epochs
        for epoch in range(self.config.n_epochs):
            logger.info("=====================================================")
            logger.info(
                f"On training epoch {epoch}/{self.config.n_epochs} ({float(epoch) / float(self.config.n_epochs) * 100.0}%)")

            if self.config.trainer_type == ModelTrainerTypeEnum.PYTORCH_OBJECT_DETECTOR:
                metric_logger = self._on_training_epoch(
                    epoch=epoch,
                    train_data=train_data,
                    train_loss=self.train_loss,
                    train_acc=self.train_acc, **kwargs)

                logger.info("=====================================================")
                return metric_logger
            else:
                train_loss_result, avg_train_epoch_loss, \
                avg_train_epoch_accuracy = self._on_training_epoch(
                    epoch=epoch,
                    train_data=train_data,
                    train_loss=self.train_loss,
                    train_acc=self.train_acc, **kwargs)

                executed_epochs += 1

                if self.config.lr_scheduler is not None:
                    self.config.lr_scheduler.step()

                logger.info(
                    f'Epoch average (over batches) train metrics '
                    f'loss/accuracy: {avg_train_epoch_loss}/{avg_train_epoch_accuracy}')
                if validate_data is not None:
                    best_acc, best_state, avg_val_epoch_loss, avg_val_epoch_accuracy = \
                        self._on_validation_epoch(validate_data=validate_data,
                                                  val_loss=self.val_loss,
                                                  val_acc=self.val_acc, best_acc=best_acc,
                                                  best_state=best_state, **kwargs)

                    logger.info(
                        f'Epoch average (over batches) validation metrics '
                        f'loss/accuracy: {avg_val_epoch_loss}/{avg_val_epoch_accuracy}')
                    logger.info(f'Best accuracy: {best_acc}')

                logger.info("=====================================================")

        info = TrainInfo(executed_epochs=executed_epochs,
                         on_device_type=self.config.device,
                         best_accuracy=best_acc,
                         train_loss=self.train_loss,
                         train_accuracy=self.train_acc,
                         validate_loss=self.val_loss,
                         validate_accuracy=self.val_acc,
                         trainer_config=self.config)

        return info

    def _on_training_epoch(self, epoch: int,
                           train_data: DataLoader, train_loss: List[float],
                           train_acc: List[float], **kwargs) -> Union[tuple | mir_vision_utils.MetricLogger]:

        """Execute a training epoch

        Parameters
        ----------
        train_data: The data to train on
        train_loss: Buffer for train loss monitoring
        train_acc: Buffer for test loss monitoring

        Returns
        -------

        """

        # set the model for training
        self.config.model.train()

        if self.config.trainer_type == ModelTrainerTypeEnum.PYTORCH_OBJECT_DETECTOR:
            metric_logger = self._model_train_epoch_with_mask(epoch=epoch,
                                                              train_data=train_data)
            return metric_logger
        else:

            epoch_loss = []
            epoch_accuracy = []

            loss_result: LossFuncResult = None

            if self.config.trainer_type == ModelTrainerTypeEnum.PYTORCH_PROTOTYPICAL_CLASSIFIER:
                self.config.application_train_fit(model=self.config.model,
                                                  data=train_data,
                                                  optimizer=self.config.optimizer,
                                                  criterion=self.config.loss_func,
                                                  epoch_loss=epoch_loss,
                                                  epoch_accuracy=epoch_accuracy,
                                                  device=self.config.device)
                avg_epoch_loss = np.mean(epoch_loss)
                avg_epoch_accuracy = np.mean(epoch_accuracy)
                train_acc.append(avg_epoch_accuracy)
                train_loss.append(avg_epoch_loss)
                return loss_result, avg_epoch_loss, avg_epoch_accuracy

            if self.config.application_train_fit is not None:
                self.config.application_train_fit(model=self.config.model,
                                                  data=train_data,
                                                  optimizer=self.config.optimizer,
                                                  criterion=self.config.loss_func,
                                                  epoch_loss=epoch_loss,
                                                  epoch_accuracy=epoch_accuracy,
                                                  device=self.config.device)
            else:
                self._model_train_epoch_fit(train_data=train_data,
                                            epoch_loss=epoch_loss,
                                            epoch_accuracy=epoch_accuracy,
                                            train_loss=train_loss,
                                            train_acc=train_acc, **kwargs)

            avg_epoch_loss = np.mean(epoch_loss)
            avg_epoch_accuracy = np.mean(epoch_accuracy)
            train_acc.append(avg_epoch_accuracy)
            train_loss.append(avg_epoch_loss)
            return loss_result, avg_epoch_loss, avg_epoch_accuracy

    def _on_validation_epoch(self, validate_data: DataLoader, val_loss: List[float],
                             val_acc: List[float], best_acc: float, best_state: dict,
                             **kwargs) -> Union[tuple | CocoEvaluator]:
        """Performs one validation epoch

        Parameters
        ----------
        validate_data: The data to validate against
        val_loss
        val_acc
        best_acc: The best running accuracy

        Returns
        -------

        """

        if self.config.clear_cuda_cache_on_validation:
            torch.cuda.empty_cache()

        epoch_loss = []
        epoch_accuracy = []

        validate_loss_result: LossFuncResult = None

        # eval mode affects the behaviour of
        # some layers (such as batch normalization or dropout)
        self.config.model.eval()
        kwargs['best_accuracy'] = best_acc

        if self.config.trainer_type == ModelTrainerTypeEnum.PYTORCH_OBJECT_DETECTOR:
            return self._model_validate_epoch_with_mask(epoch=0,
                                                        validate_data=validate_data)

        else:

            if self.config.trainer_type == ModelTrainerTypeEnum.PYTORCH_PROTOTYPICAL_CLASSIFIER:
                prototypes = self.config.application_validation_fit(model=self.config.model,
                                                                    data=validate_data,
                                                                    criterion=self.config.loss_func_validate,
                                                                    epoch_loss=epoch_loss,
                                                                    epoch_accuracy=epoch_accuracy,
                                                                    device=self.config.device,
                                                                    **kwargs)

                avg_epoch_loss = np.mean(epoch_loss)
                avg_epoch_accuracy = np.mean(epoch_accuracy)
                val_loss.append(avg_epoch_loss)
                val_acc.append(avg_epoch_accuracy)

                if avg_epoch_accuracy >= best_acc:
                    if self.config.save_best_model:
                        torch.save(self.config.model.state_dict(), self.config.best_model_path)

                    if self.config.save_model_prototypes_on_validation:

                        if prototypes is None:
                            raise ValueError(f"You chose to save validation prototypes "
                                             "but the returned prototypes are None.")

                        try:
                            prototypes_length = len(prototypes)
                        except TypeError as e:
                            raise ValueError(f"You chose to save validation prototypes "
                                             "but the returned prototypes have zero length")
                        torch.save(prototypes, self.config.best_accuracy_prototypes_filepath)

                    best_acc = avg_epoch_accuracy
                    best_state = copy.deepcopy(self.config.model.state_dict())

                return best_acc, best_state, avg_epoch_loss, avg_epoch_accuracy

            if self.config.application_validation_fit is not None:

                self.config.application_validation_fit(model=self.config.model,
                                                       data=validate_data,
                                                       criterion=self.config.loss_func_validate,
                                                       epoch_loss=epoch_loss,
                                                       epoch_accuracy=epoch_accuracy,
                                                       device=self.config.device,
                                                       **kwargs)

            else:
                self._model_validation_epoch_fit(validate_data=validate_data,
                                                 epoch_loss=epoch_loss,
                                                 epoch_accuracy=epoch_accuracy,
                                                 val_loss=val_loss,
                                                 val_acc=val_acc, **kwargs)

            avg_epoch_loss = np.mean(epoch_loss)
            avg_epoch_accuracy = np.mean(epoch_accuracy)
            val_loss.append(avg_epoch_loss)
            val_acc.append(avg_epoch_accuracy)

            if avg_epoch_accuracy >= best_acc:
                if self.config.save_best_model:
                    torch.save(self.config.model.state_dict(), self.config.best_model_path)

                best_acc = avg_epoch_accuracy
                best_state = copy.deepcopy(self.config.model.state_dict())

            return best_acc, best_state, avg_epoch_loss, avg_epoch_accuracy

    def _model_train_epoch_fit(self, train_data: DataLoader, epoch_loss: List[float],
                               epoch_accuracy: List[float], train_loss: List[float],
                               train_acc: List[float], **kwargs):

        for batch, x, y in tqdm(enumerate(train_data),
                                total=len(train_data),
                                desc="Training"):  # enumerate(train_data, 0):

            # get the inputs; datasets is a list of [inputs, labels]
            x, y = x, y

            # send the received data to the device
            x = x.to(self.config.device)
            y = y.to(self.config.device)

            # zero the parameter gradients
            self.config.optimizer.zero_grad()

            # forward pass
            outputs = self.config.model(x)

            # compute loss and do a backward pass
            loss_result: LossFuncResult = self.config.loss_func(outputs, y)

            if isinstance(loss_result, torch.Tensor):
                loss_result.backward()
            else:
                loss_result.loss.backward()

            # optimize
            self.config.optimizer.step()

            epoch_loss.append(loss_result.loss.item())
            _, preds = torch.max(outputs, 1)

            batch_accuracy = torch.sum(preds == y.data).item() / float(len(y.data))
            epoch_accuracy.append(batch_accuracy)

            logger.info(f"For training batch={batch} accuracy={batch_accuracy}")

    def _model_validation_epoch_fit(self, validate_data: DataLoader, epoch_loss: List[float],
                                    epoch_accuracy: List[float], val_loss: List[float],
                                    val_acc: List[float], **kwargs):

        # val_iter = iter(validate_data)

        # no_grad() tells torch not to keep in memory
        # the whole computational graph (it's more lightweight this way)
        with torch.no_grad():
            for batch, (x, y) in tqdm(enumerate(validate_data), total=len(validate_data),
                                      desc="Validation"):  # batch in val_iter:
                x, y = x, y
                x = x.to(self.config.device)
                y = y.to(self.config.device)
                outputs = self.config.model(x)
                validate_loss_result: LossFuncResult = self.config.loss_func_validate(outputs, y)

                # we append the average epoch loss as the train loss
                epoch_loss.append(validate_loss_result.loss.item())
                _, preds = torch.max(outputs, 1)
                batch_accuracy = torch.sum(preds == y.data).item() / float(len(y.data))
                epoch_accuracy.append(batch_accuracy)
                logger.info(f"For validation batch={batch} accuracy={batch_accuracy}")

    def _model_train_epoch_with_mask(self, epoch, train_data, **kwargs) -> mir_vision_utils.MetricLogger:

        metric_logger = train_one_epoch(model=self.config.model,
                                        optimizer=self.config.optimizer,
                                        data_loader=train_data,
                                        device=self.config.device,
                                        epoch=epoch,
                                        print_freq=10, scaler=None)
        return metric_logger

    def _model_validate_epoch_with_mask(self, epoch, validate_data, **kwargs) -> CocoEvaluator:
        coco_evaluator = evaluate(model=self.config.model,
                                  data_loader=validate_data,
                                  device=self.config.device)
        return coco_evaluator
