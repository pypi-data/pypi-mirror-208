"""module trainer_wrapper. Utility class that
wraps the train/test process for two-class classification

"""
from typing import Callable
from pathlib import Path
from loguru import logger
import mlflow

import torch
from torch.utils.data import DataLoader
import torch.nn as nn
from torchsummary import summary

from mir_ml_utils.models import ModelAdaptorTypeEnum
from mir_ml_utils.trainers.pytorch_trainer import PyTorchTrainer, PyTorchTrainerConfig

from mir_ml_utils.factories.optimzer_factory import build_optimizer
from mir_ml_utils.factories.loss_function_factory import build_loss_function
from mir_ml_utils.factories.model_builder_factory import model_builder
from mir_ml_utils.loss_functions.loss_function_wrapper import LossFunctionWrapper
from mir_ml_utils.factories.model_adaptor_factory import model_adaptor_builder
from mir_ml_utils.utils.math_ops import set_seed
from mir_ml_utils.trainers.trainer_wrapper_pimpl import TrainerWrapperPimpl
from mir_ml_utils.trainers.model_trainer_type_enum import ModelTrainerTypeEnum


class TrainerWrapper(object):

    def __init__(self, config: dict):

        self.pimpl = TrainerWrapperPimpl(config=config)
        self.config = config
        self.simulation_data_dir_output: Path = Path("")
        self.device = 'cpu'

    def run(self, model: nn.Module = None,
            train_pipeline: Callable = None,
            val_pipeline: Callable = None,
            mask_transformer: Callable = None,
            train_data: DataLoader = None,
            validate_data: DataLoader = None):

        set_seed(seed=self.pimpl.config['seed'])
        app_name = self.pimpl.config["app_name"]
        run_name = self.pimpl.config["run_name"]

        run_dir_output = Path(self.pimpl.config["run_dir_output"])
        log_filename = self.pimpl.config['log_filename']
        rotation_file_log_size = self.pimpl.config['rotation_file_log_size']

        with mlflow.start_run(run_name=str(run_name)) as mlflow_run:
            self.pimpl.create_dirs()

            self.device = 'cuda:0' if torch.cuda.is_available() and self.config['train_options']['use_cuda'] else 'cpu'
            self.simulation_data_dir_output = run_dir_output / run_name

            # tmp fix
            self.pimpl.device = self.device
            self.pimpl.simulation_data_dir_output = self.simulation_data_dir_output

            logger.add(self.simulation_data_dir_output / log_filename,
                       rotation=rotation_file_log_size)
            logger.info(f"Starting simulation. Output directory={self.pimpl.simulation_data_dir_output}")
            logger.info(f"Running app {app_name}")
            logger.info(f"Using device {self.pimpl.device}")

            mlflow.log_param("App_name", app_name)
            mlflow.log_param("device", self.pimpl.device)

            if train_data is None and validate_data is None:
                logger.warning("Train data and validate data is None...Loading from configuration file")
                train_dataloader, x_train_size, validation_dataloader, x_validate_size = self.load_data(
                    train_pipeline=train_pipeline,
                    val_pipeline=val_pipeline,
                    masks_transformer=mask_transformer)
                self.train_loop(model=model,
                                train_data=train_dataloader, validate_data=validation_dataloader)
            elif train_data is None and validate_data is not None:
                raise ValueError("Train data is None  but validation data is not")
            else:
                self.train_loop(model=model,
                                train_data=train_data, validate_data=validate_data)

    def load_data(self, train_pipeline: Callable = None,
                  val_pipeline: Callable = None,
                  masks_transformer: Callable = None):

        return self.pimpl.do_load_train_data(val_transformers=val_pipeline,
                                             train_transformers=train_pipeline,
                                             options={'masks_transformers': masks_transformer})

    def train_loop(self, model: nn.Module,
                   train_data: DataLoader, validate_data: DataLoader):

        if model is None:
            logger.warning(f"Application model is None. building model")

            model_adaptor_options = {"n_classes": self.config['train_options']['n_classes']}

            if self.config['test_options']['model_adaptor']['name'] != ModelAdaptorTypeEnum.NONE:
                model_adaptor_options.update(self.config['train_options']['model_adaptor']["properties"])

            model_adaptor = model_adaptor_builder(
                adaptor_type=self.config['train_options']['model_adaptor']['name'],
                options=model_adaptor_options)

            model = model_builder(builder_name=self.pimpl.config['train_options']['model_builder_factory'],
                                  config={'model_type': self.pimpl.config['train_options']['model_type'],
                                          'model_adaptor': model_adaptor,
                                          'device': self.pimpl.device,
                                          'with_pretrained': self.pimpl.config['train_options']['with_pretrained'],
                                          'freeze_model_parameters': self.pimpl.config['train_options'][
                                              'freeze_model_parameters'],
                                          "n_classes": self.pimpl.config['train_options']['n_classes']})

        if model is None:
            logger.error(f"Model is None")
            raise ValueError("Model is None")

        logger.info(summary(model))

        if self.pimpl.config['train_options']['with_pretrained']:
            params_to_update = [p for p in model.parameters() if p.requires_grad]
        else:
            params_to_update = model.parameters()

        mlflow.log_param("optimizer", self.pimpl.config['train_options']['optimizer']['name'])
        mlflow.log_param("learning_rate", self.pimpl.config['train_options']['optimizer']['learning_rate'])
        mlflow.log_param("weight_decay", self.pimpl.config['train_options']['optimizer']['weight_decay'])
        mlflow.log_param("batch_size", self.pimpl.config['train_options']['batch_size'])
        mlflow.log_param("n_epochs", self.pimpl.config['train_options']['n_epochs'])
        mlflow.log_param("validation_size", self.pimpl.config['validation_options']['validation_size'])
        mlflow.log_param("seed", self.pimpl.config['seed'])
        mlflow.log_param("num_workers", self.pimpl.config['train_options']['num_workers'])

        # create the optimizer
        optimizer = build_optimizer(model_params=params_to_update,
                                    config=self.pimpl.config['train_options']['optimizer'])

        loss = LossFunctionWrapper(loss=build_loss_function(config=self.pimpl.config['train_options']['loss_function']))

        trainer_config = self._build_trainer_config(model=model, loss=loss,
                                                    optimizer=optimizer)

        # create the trainer
        trainer = PyTorchTrainer(config=trainer_config)

        # conceptualize saving individual trainer
        # configs and their various results, compare metrics and select best model
        # assign best model
        train_info = trainer.fit(train_data=train_data, validate_data=validate_data)
        self.pimpl.save_validation_train_files(trainer=trainer, train_info=train_info)
        logger.info("Model training finished...")

    def load_test_set(self, test_data_transforms: Callable, options: dict):

        logger.info("Loading test dataset")
        return self.pimpl.do_load_test_data(test_transformers=test_data_transforms,
                                            options=options)

    def _build_trainer_config(self, model, optimizer, loss):

        if self.config["train_options"]["trainer_type"] == ModelTrainerTypeEnum.PYTORCH_OBJECT_DETECTOR:
            trainer_config = PyTorchTrainerConfig(model=model,
                                                  model_name=self.config['model_name'],
                                                  optimizer=optimizer,
                                                  loss_func=loss,
                                                  loss_func_validate=loss,
                                                  n_epochs=self.config['train_options']['n_epochs'],
                                                  save_best_model=self.config['train_options']['save_best_model'],
                                                  model_registry_path=self.simulation_data_dir_output,
                                                  best_model_path=self.simulation_data_dir_output / self.config[
                                                      'best_model_name'],
                                                  device=self.device,
                                                  lr_scheduler=None,
                                                  application_train_fit=
                                                  self.config['train_options']['few_shot_options']['epoch_fit_model'],
                                                  application_validation_fit=
                                                  self.config['validation_options']['few_shot_options'][
                                                      'epoch_validation_fit_model'],
                                                  trainer_type=self.config["train_options"]["trainer_type"]
                                                  )

        elif self.config['train_options']['trainer_type'] == ModelTrainerTypeEnum.PYTORCH_PROTOTYPICAL_CLASSIFIER:

            if 'epoch_fit_model' not in self.config['train_options']['few_shot_options'] or \
                    'epoch_validation_fit_model' not in self.config['validation_options']['few_shot_options']:
                raise ValueError(f"Invalid few show configuration")

            trainer_config = PyTorchTrainerConfig(model=model,
                                                  model_name=self.config['model_name'],
                                                  optimizer=optimizer,
                                                  loss_func=loss,
                                                  loss_func_validate=loss,
                                                  n_epochs=self.config['train_options']['n_epochs'],
                                                  save_best_model=self.config['train_options']['save_best_model'],
                                                  model_registry_path=self.simulation_data_dir_output,
                                                  best_model_path=self.simulation_data_dir_output / self.config[
                                                      'best_model_name'],
                                                  device=self.device,
                                                  lr_scheduler=None,
                                                  application_train_fit=
                                                  self.config['train_options']['few_shot_options']['epoch_fit_model'],
                                                  application_validation_fit=
                                                  self.config['validation_options']['few_shot_options'][
                                                      'epoch_validation_fit_model'],
                                                  best_accuracy_prototypes_filepath=
                                                  self.pimpl.simulation_data_dir_output /
                                                  self.config['validation_options']
                                                  ['few_shot_options']['validation_prototypes_name'],
                                                  save_model_prototypes_on_validation=True,
                                                  trainer_type=self.config["train_options"]["trainer_type"]
                                                  )

        elif self.config["train_options"]["trainer_type"] == ModelTrainerTypeEnum.PYTORCH_CLASSIFIER:

            trainer_config = PyTorchTrainerConfig(model=model,
                                                  model_name=self.config['model_name'],
                                                  optimizer=optimizer,
                                                  loss_func=loss,
                                                  loss_func_validate=loss,
                                                  n_epochs=self.config['train_options']['n_epochs'],
                                                  save_best_model=self.config['train_options']['save_best_model'],
                                                  model_registry_path=self.simulation_data_dir_output,
                                                  best_model_path=self.simulation_data_dir_output / self.config[
                                                      'best_model_name'],
                                                  device=self.device,
                                                  lr_scheduler=None,
                                                  trainer_type=self.config["train_options"]["trainer_type"])

        else:
            raise ValueError(f" 'trainer_type' {self.config['train_options']['trainer_type']} "
                             f"not in ['CLASSIFIER', 'FEW_SHOT_CLASSIFIER', 'OBJECT_DETECTOR']")

        return trainer_config
