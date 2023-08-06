from pathlib import Path
from typing import Callable, List
from loguru import logger
from torch.utils.data import DataLoader, WeightedRandomSampler
import torch.nn as nn
import torch
import mlflow
from sklearn.model_selection import train_test_split
import numpy as np

from mir_ml_utils.utils.mode_enum import ModeEnum
import mir_ml_utils.data_handlers.img_utils as img_utils
import mir_ml_utils.mir_vision.references.detection.utils as vision_utils
from mir_ml_utils.mir_vision.references.detection.engine import evaluate
from mir_ml_utils.utils.file_utils import create_dir
from mir_ml_utils.utils.function_wrappers import time_func_wrapper
from mir_ml_utils.testers.two_class_model_tester_wrapper import TwoClassPyTorchModelTester
from mir_ml_utils.factories.model_adaptor_factory import model_adaptor_builder
from mir_ml_utils.factories.model_builder_factory import model_loader
from mir_ml_utils.utils.file_utils import save_as_pickle, save_list_as_csv
from mir_ml_utils.data_handlers.dataset_with_masks import DatasetWithMasks
from mir_ml_utils.data_handlers.images_dataset import ImagesDataset
from mir_ml_utils.easyfsl.samplers.task_sampler import TaskSampler


class TrainerWrapperPimpl(object):

    def __init__(self, config: dict):
        self.config = config
        self.simulation_data_dir_output: Path = Path("")
        self.device = 'cpu'

    def create_dirs(self):

        run_dir_output = Path(self.config["run_dir_output"])
        run_name = self.config["run_name"]
        try:
            create_dir(path=run_dir_output, dirname=str(run_name))
        except ValueError as e:
            print(str(e))
            pass

        if self.config['test_options']['with_simple_segmentation']:
            try:
                create_dir(path=run_dir_output / run_name,
                           dirname=self.config['test_options']['simple_segmentation_out'])
            except ValueError as e:
                print(str(e))
                pass

    def do_load_train_data(self, val_transformers: Callable, train_transformers: Callable,
                           options: dict):
        if self.config['train_options']['trainer_type'] == 'OBJECT_DETECTOR':

            data, _ = self.create_train_validate_datasets_with_mask(
                train_transformers=train_transformers,
                val_transformers=val_transformers,
                masks_transformers=options['masks_transformers'])

            train_dataloader = data[0]
            x_train_size = data[1]
            validation_dataloader = data[2]
            x_validate_size = data[3]
            return train_dataloader, x_train_size, validation_dataloader, x_validate_size
        elif self.config['train_options']['trainer_type'] == 'CLASSIFIER':

            data, _ = self.create_train_validate_classifier_datasets(
                val_transformers=val_transformers,
                train_transformers=train_transformers)

            train_dataloader = data[0]
            x_train_size = data[1]
            validation_dataloader = data[2]
            x_validate_size = data[3]
            return train_dataloader, x_train_size, validation_dataloader, x_validate_size
        elif self.config['train_options']['trainer_type'] == 'FEW_SHOT_CLASSIFIER':

            data, _ = self.create_few_shot_classifier_train_validate_datasets(
                val_transformers=val_transformers,
                train_transformers=train_transformers)

            train_dataloader = data[0]
            x_train_size = data[1]
            validation_dataloader = data[2]
            x_validate_size = data[3]
            return train_dataloader, x_train_size, validation_dataloader, x_validate_size,
        else:
            raise ValueError(f"{self.config['test_options']['tester_type']} is an invalid tester type")

    def do_load_test_data(self, test_transformers: Callable, options: dict):

        if self.config['test_options']['tester_type'] == 'OBJECT_DETECTOR':
            test_data, _ = self.create_object_localization_test_data(test_transformers=test_transformers,
                                                                     mask_transformers=options['mask_transformers'],
                                                                     exclude_names=options['exclude_names'])
            return test_data
        elif self.config['test_options']['tester_type'] == 'CLASSIFIER':

            test_data, _ = self.create_classifier_model_test_data(test_transformers=test_transformers)
            return test_data
        elif self.config['test_options']['tester_type'] == 'FEW_SHOT_CLASSIFIER':
            test_data, _ = self.create_few_shot_classifier_model_test_data(test_transformers=test_transformers)
            return test_data
        else:
            raise ValueError(f"{self.config['test_options']['tester_type']} is an invalid tester type")

    def do_model_test(self, model: nn.Module, test_set: DataLoader):

        if self.config['test_options']['tester_type'] == 'OBJECT_DETECTOR':
            return self.do_object_localization_model_test(model=model, test_set=test_set)
        elif self.config['test_options']['tester_type'] == 'CLASSIFIER':
            return self.do_classifier_model_test(model=model, test_set=test_set)
        elif self.config['test_options']['tester_type'] == 'FEW_SHOT_CLASSIFIER':
            return self.do_few_shot_classifier_model_test(model=model, test_set=test_set)
        else:
            raise ValueError(f"{self.config['test_options']['tester_type']} is an invalid tester type")

    @time_func_wrapper(show_time=True)
    def do_object_localization_model_test(self, model: nn.Module, test_set: DataLoader):
        logger.info("Testing object localization model...")
        evaluate(model=model, data_loader=test_set, device=self.device)
        logger.info("Done...")

    @time_func_wrapper(show_time=True)
    def do_classifier_model_test(self, model: nn.Module, test_set: DataLoader):
        logger.info("Testing classifier model...")
        if model is None:
            logger.info(f"Application model is None. building model")

            model = model_loader(builder_name=self.config['train_options']['model_builder_factory'],
                                 config={'model_type': self.config['train_options']['model_type'],
                                         'model_path': self.simulation_data_dir_output / self.config['best_model_name'],
                                         'model_adaptor': model_adaptor_builder(
                                             adaptor_type=self.config['test_options']['model_adaptor'],
                                             options={"n_classes": self.config['train_options']['n_classes']}),
                                         'device': self.device,
                                         'with_pretrained': self.config['train_options']['with_pretrained'],
                                         'freeze_model_parameters': self.config['train_options'][
                                             'freeze_model_parameters']})

        model.eval()

        run_name = self.config["run_name"]
        run_dir_output = Path(self.config["run_dir_output"])

        if self.config['test_options']['tester_type'] == "CLASSIFIER":

            options = {'device': self.device,
                       'class0_name': self.config['class_0_name'],
                       'class1_name': self.config['class_1_name'],
                       'create_simple_segmentation': self.config['test_options']['with_simple_segmentation'],
                       'test_class_0_images_path': Path(
                           self.config['data_dir']) / "test" / self.config[
                                                       "class_0_name"],
                       'test_class_1_images_path': Path(
                           self.config['data_dir']) / "test" / self.config[
                                                       "class_1_name"],
                       'img_shape': self.config['test_options']['img_shape'],
                       'simple_segmentation_out': run_dir_output / run_name /
                                                  self.config['test_options'][
                                                      'simple_segmentation_out'],
                       'img_transform': None,
                       'class1_threshold': self.config['test_options'][
                           'class1_threshold'],
                       "evaluate_few_shot_learner": False}
        elif self.config['test_options']['tester_type'] == "FEW_SHOT_CLASSIFIER":

            options = {'device': self.device,
                       'class0_name': self.config['class_0_name'],
                       'class1_name': self.config['class_1_name'],
                       'create_simple_segmentation': self.config['test_options']['with_simple_segmentation'],
                       'test_class_0_images_path': Path(
                           self.config['data_dir']) / "test" / self.config[
                                                       "class_0_name"],
                       'test_class_1_images_path': Path(
                           self.config['data_dir']) / "test" / self.config[
                                                       "class_1_name"],
                       'img_shape': self.config['test_options']['img_shape'],
                       'simple_segmentation_out': run_dir_output / run_name /
                                                  self.config['test_options'][
                                                      'simple_segmentation_out'],
                       'img_transform': None,
                       'class1_threshold': self.config['test_options'][
                           'class1_threshold'],
                       "evaluate_few_shot_learner": True,
                       "few_shot_inference_with": self.config['test_options']['few_shot_options']['inference_with'],
                       "few_shot_prototypes_file_path": self.simulation_data_dir_output / self.config['test_options']['few_shot_options']['prototypes_names']}
        else:
            ValueError(f"tester type {self.config['test_options']['tester_type']} is not implemented")

        two_class_tester = TwoClassPyTorchModelTester(options=options)

        two_class_tester.evaluate(model=model, dataloader=test_set)
        logger.info("Done...")

    @time_func_wrapper(show_time=True)
    def do_few_shot_classifier_model_test(self, model: nn.Module, test_set: DataLoader):
        logger.info("Testing classifier model...")
        self.do_classifier_model_test(model=model, test_set=test_set)
        logger.info("Done...")

    @time_func_wrapper(show_time=True)
    def create_train_validate_classifier_datasets(self, val_transformers: Callable, train_transformers: Callable):
        logger.info("Loading classifier dataset...")

        class_0_path = Path(self.config['data_dir']) / "train" / self.config["class_0_name"]
        class_1_path = Path(self.config['data_dir']) / "train" / self.config["class_1_name"]

        if str(class_0_path) == str(class_1_path):
            raise ValueError(f"Same path for {self.config['class_0_name']} and "
                             f" {self.config['class_1_name']} data")

        logger.info(f"class 0={self.config['class_0_name']} data path = {class_0_path}")
        logger.info(f"class 1={self.config['class_1_name']} data path = {class_1_path}")

        if self.config["data_type"] == "images":

            # let's get all the files
            train_class_0_data = img_utils.get_img_files(img_dir=class_0_path,
                                                         img_formats=['jpg', 'png', 'jpeg'],
                                                         with_batch_structure=self.config['with_batches'])

            train_class_1_data = img_utils.get_img_files(img_dir=class_1_path,
                                                         img_formats=['jpg', 'png', 'jpeg'],
                                                         with_batch_structure=self.config['with_batches']
                                                         )

            if self.config['train_options']['max_train_size'] != 'all':
                logger.info(f"Limiting train data to size={self.config['train_options']['max_train_size']}")

                train_class_0_data = np.random.choice(train_class_0_data,
                                                      size=self.config['train_options']['max_train_size'],
                                                      replace=False).tolist()

                train_class_1_data = np.random.choice(train_class_1_data,
                                                      size=self.config['train_options']['max_train_size'],
                                                      replace=False).tolist()

            logger.info(f"Number of train {self.config['class_0_name']} images {len(train_class_0_data)}")
            logger.info(f"Number of train {self.config['class_1_name']} images {len(train_class_1_data)}")

            if self.config['validate_state']:
                assert len(train_class_0_data) == self.config['train_options']['train_class_0_data_size'], \
                    f"Invalid number of train {self.config['class_0_name']} images "

                assert len(train_class_1_data) == self.config['train_options']['train_class_1_data_size'], \
                    f"Invalid number of train {self.config['class_1_name']} images"
        else:
            raise ValueError(f"Invalid data type={self.config['data_types']}")

        train_val_images = train_class_1_data + train_class_0_data
        labels = [1] * len(train_class_1_data) + [0] * len(train_class_0_data)
        x_train, x_validate, x_train_labels, x_val_labels = train_test_split(train_val_images, labels,
                                                                             test_size=self.config["validation_size"],
                                                                             random_state=self.config['seed'],
                                                                             shuffle=self.config['shuffle'])

        logger.info(f"Train set size {len(x_train)}")
        logger.info(f"Validation set size {len(x_validate)}")

        # create the datasets
        train_set = ImagesDataset.from_file_sources(filenames=x_train,
                                                    labels=x_train_labels,
                                                    mode=ModeEnum.TRAIN,
                                                    on_load_transformers=train_transformers)

        val_set = ImagesDataset.from_file_sources(filenames=x_validate,
                                                  labels=x_val_labels,
                                                  mode=ModeEnum.VALIDATE,
                                                  on_load_transformers=val_transformers)

        if self.config['train_options']['dataloader']['has_imbalanced_classes']:
            class_weights = self.config['train_options']['dataloader']['class_weights']
            sample_weights = [0] * len(train_set)

            for idx, (data, label) in enumerate(train_set):
                cls_weight = class_weights[label]
                sample_weights[idx] = cls_weight

            sampler = WeightedRandomSampler(weights=sample_weights,
                                            replacement=True,
                                            num_samples=self.config['batch_size'])

            # Remark cannot specify shuffle when
            # specifying sampler.
            # ValueError: sampler option is mutually exclusive with shuffle
            train_dataloader = torch.utils.data.DataLoader(train_set,
                                                           sampler=sampler,
                                                           batch_size=self.config['batch_size'],
                                                           # shuffle=self.config['shuffle'],
                                                           num_workers=self.config['num_workers'])
        else:

            train_dataloader = torch.utils.data.DataLoader(train_set,
                                                           batch_size=self.config['batch_size'],
                                                           shuffle=self.config['shuffle'],
                                                           num_workers=self.config['num_workers'])

        validation_dataloader = torch.utils.data.DataLoader(val_set,
                                                            batch_size=self.config['batch_size'],
                                                            shuffle=self.config['shuffle'],
                                                            num_workers=self.config['num_workers'])

        logger.info("Done...")
        return train_dataloader, len(x_train), validation_dataloader, len(x_validate)

    @time_func_wrapper(show_time=True)
    def create_few_shot_classifier_train_validate_datasets(self, val_transformers: Callable,
                                                           train_transformers: Callable):

        class_0_path = Path(self.config['data_dir']) / "train" / self.config["class_0_name"]
        class_1_path = Path(self.config['data_dir']) / "train" / self.config["class_1_name"]

        if str(class_0_path) == str(class_1_path):
            raise ValueError(f"Same path for {self.config['class_0_name']} and "
                             f" {self.config['class_1_name']} data")

        logger.info(f"class 0={self.config['class_0_name']} data path = {class_0_path}")
        logger.info(f"class 1={self.config['class_1_name']} data path = {class_1_path}")

        if self.config["data_type"] == "images":

            # let's get all the files
            train_class_0_data = img_utils.get_img_files(img_dir=class_0_path,
                                                         img_formats=['jpg', 'png', 'jpeg'],
                                                         with_batch_structure=self.config['with_batches'])

            train_class_1_data = img_utils.get_img_files(img_dir=class_1_path,
                                                         img_formats=['jpg', 'png', 'jpeg'],
                                                         with_batch_structure=self.config['with_batches']
                                                         )

            if self.config['train_options']['max_train_size'] != 'all':
                logger.info(f"Limiting train data to size={self.config['train_options']['max_train_size']}")

                train_class_0_data = np.random.choice(train_class_0_data,
                                                      size=self.config['train_options']['max_train_size'],
                                                      replace=False).tolist()

                train_class_1_data = np.random.choice(train_class_1_data,
                                                      size=self.config['train_options']['max_train_size'],
                                                      replace=False).tolist()

            logger.info(f"Number of train {self.config['class_0_name']} images {len(train_class_0_data)}")
            logger.info(f"Number of train {self.config['class_1_name']} images {len(train_class_1_data)}")

            if self.config['validate_state']:
                assert len(train_class_0_data) == self.config['train_options']['train_class_0_data_size'], \
                    f"Invalid number of train {self.config['class_0_name']} images "

                assert len(train_class_1_data) == self.config['train_options']['train_class_1_data_size'], \
                    f"Invalid number of train {self.config['class_1_name']} images"
        else:
            raise ValueError(f"Invalid data type={self.config['data_types']}")

        train_val_images = train_class_1_data + train_class_0_data
        labels = [1] * len(train_class_1_data) + [0] * len(train_class_0_data)
        x_train, x_validate, x_train_labels, x_val_labels = train_test_split(train_val_images, labels,
                                                                             test_size=self.config["validation_size"],
                                                                             random_state=self.config['seed'],
                                                                             shuffle=self.config['shuffle'])

        logger.info(f"Train set size {len(x_train)}")
        logger.info(f"Validation set size {len(x_validate)}")

        # create the datasets
        train_set = ImagesDataset.from_file_sources(filenames=x_train,
                                                    labels=x_train_labels,
                                                    mode=ModeEnum.TRAIN,
                                                    on_load_transformers=train_transformers)

        val_set = ImagesDataset.from_file_sources(filenames=x_validate,
                                                  labels=x_val_labels,
                                                  mode=ModeEnum.VALIDATE,
                                                  on_load_transformers=val_transformers)

        train_batch_sampler = TaskSampler(dataset=train_set,
                                          n_way=self.config['train_options']['n_classes'],
                                          n_shot=self.config['train_options']['few_shot_options'][
                                              'n_support_pts'],
                                          n_query=self.config['train_options']['few_shot_options'][
                                              'n_query_pts'],
                                          n_tasks=self.config['train_options']['few_shot_options'][
                                              'n_iterations'])

        train_dataloader = torch.utils.data.DataLoader(train_set,
                                                       batch_sampler=train_batch_sampler,
                                                       num_workers=self.config['num_workers'],
                                                       pin_memory=True,
                                                       collate_fn=train_batch_sampler.episodic_collate_fn)

        val_batch_sampler = TaskSampler(dataset=val_set,
                                        n_way=self.config['train_options']['n_classes'],
                                        n_shot=self.config['validation_options']['few_shot_options'][
                                            'n_support_pts'],
                                        n_query=self.config['validation_options']['few_shot_options'][
                                            'n_query_pts'],
                                        n_tasks=self.config['validation_options']['few_shot_options'][
                                            'n_iterations'])

        validation_dataloader = torch.utils.data.DataLoader(val_set,
                                                            batch_sampler=val_batch_sampler,
                                                            num_workers=self.config['num_workers'],
                                                            pin_memory=True,
                                                            collate_fn=val_batch_sampler.episodic_collate_fn)
        logger.info("Done...")
        return train_dataloader, len(x_train), validation_dataloader, len(x_validate)

    @time_func_wrapper(show_time=True)
    def create_train_validate_datasets_with_mask(self, masks_transformers: Callable,
                                                 val_transformers: Callable, train_transformers: Callable) -> tuple:
        """

        Parameters
        ----------
        train_transformers
        val_transformers
        masks_transformers
        Returns
        -------

        """

        logger.info("Loading dataset with masks...")

        images_path = Path(self.config['data_dir'])
        masks_path = Path(self.config['masks_dir'])
        masks_format = self.config["masks_format"]

        # let's get all the files
        images_filename = img_utils.get_img_files(img_dir=images_path,
                                                  img_formats=['jpg', 'png', 'jpeg'],
                                                  with_batch_structure=self.config['with_batches'])

        if self.config['train_options']['max_train_size'] != 'all':
            logger.info(f"Limiting train data to size={self.config['train_options']['max_train_size']}")

            images_filename = np.random.choice(images_filename,
                                               size=self.config['train_options']['max_train_size'],
                                               replace=False).tolist()

        logger.info(f"Number of train {self.config['class_1_name']} images {len(images_filename)}")

        labels = [1] * len(images_filename)
        x_train, x_validate, x_train_labels, x_val_labels = train_test_split(images_filename, labels,
                                                                             test_size=self.config["validation_size"],
                                                                             random_state=self.config['seed'],
                                                                             shuffle=self.config['shuffle'])

        # mask files for train
        mask_train_files = []

        for filename in x_train:
            filename_ = str(filename).split("/")[-1].split(".")[0]
            filename_ += masks_format
            mask_train_files.append(masks_path / filename_)

        mask_validate_files = []

        for filename in x_validate:
            filename_ = str(filename).split("/")[-1].split(".")[0]
            filename_ += masks_format
            mask_validate_files.append(masks_path / filename_)

        train_set = DatasetWithMasks.from_file_sources(imgs_filenames=x_train,
                                                       masks_filenames=mask_train_files,
                                                       labels=[],  # x_train_labels,
                                                       mode=ModeEnum.TRAIN,
                                                       image_loader=img_utils.load_img,
                                                       mask_loader=img_utils.load_image_as_numpy,
                                                       on_load_transformers=train_transformers,
                                                       on_load_transformers_mask=masks_transformers,
                                                       only_load_files=self.config['only_load_files'])

        val_set = DatasetWithMasks.from_file_sources(imgs_filenames=x_validate,
                                                     masks_filenames=mask_validate_files,
                                                     labels=[],  # x_val_labels,
                                                     mode=ModeEnum.VALIDATE,
                                                     image_loader=img_utils.load_img,
                                                     mask_loader=img_utils.load_image_as_numpy,
                                                     on_load_transformers=val_transformers,
                                                     on_load_transformers_mask=masks_transformers,
                                                     only_load_files=self.config['only_load_files'])

        train_dataloader = torch.utils.data.DataLoader(train_set,
                                                       batch_size=self.config['batch_size'],
                                                       shuffle=self.config['shuffle'],
                                                       num_workers=self.config['num_workers'],
                                                       collate_fn=vision_utils.collate_fn)

        validation_dataloader = torch.utils.data.DataLoader(val_set,
                                                            batch_size=self.config['batch_size'],
                                                            shuffle=self.config['shuffle'],
                                                            num_workers=self.config['num_workers'],
                                                            collate_fn=vision_utils.collate_fn)

        logger.info("Done...")
        return train_dataloader, len(x_train), validation_dataloader, len(x_validate)

    @time_func_wrapper(show_time=True)
    def create_classifier_model_test_data(self, test_transformers: Callable) -> DataLoader:
        class_0_path = Path(self.config['data_dir']) / "test" / self.config["class_0_name"]
        class_1_path = Path(self.config['data_dir']) / "test" / self.config["class_1_name"]

        if str(class_0_path) == str(class_1_path):
            raise ValueError(f"Same path for {self.config['class_0_name']} and "
                             f" {self.config['class_1_name']} data")

        if self.config["data_type"] == "images":
            # let's get all the files
            test_class_0_data = img_utils.get_img_files(img_dir=class_0_path,
                                                        img_formats=['jpg', 'png', 'jpeg'],
                                                        with_batch_structure=self.config['with_batches']
                                                        )

            test_class_1_data = img_utils.get_img_files(img_dir=class_1_path,
                                                        img_formats=['jpg', 'png', 'jpeg'],
                                                        with_batch_structure=self.config['with_batches']
                                                        )

            if self.config['test_options']['max_test_size'] != 'all':
                logger.info(f"Limiting test data to size={self.config['train_options']['max_train_size']}")

                test_class_0_data = np.random.choice(test_class_0_data,
                                                     size=self.config['train_options']['max_train_size'],
                                                     replace=False).tolist()
                test_class_1_data = np.random.choice(test_class_1_data,
                                                     size=self.config['train_options']['max_train_size'],
                                                     replace=False).tolist()

            logger.info(f"Number of test {self.config['class_0_name']} images {len(test_class_0_data)}")
            logger.info(f"Number of test {self.config['class_1_name']} images {len(test_class_1_data)}")

        else:
            raise ValueError(f"Invalid data type={self.config['data_types']}")

        test_images = test_class_1_data + test_class_0_data
        labels = [1] * len(test_class_1_data) + [0] * len(test_class_0_data)

        logger.info(f"Train set size {len(test_images)}")

        # create the datasets
        test_set = ImagesDataset.from_file_sources(filenames=test_images,
                                                   labels=labels,
                                                   on_load_transformers=test_transformers)

        test_dataloader = torch.utils.data.DataLoader(test_set,
                                                      batch_size=self.config['batch_size'],
                                                      shuffle=self.config['shuffle'],
                                                      num_workers=self.config['num_workers'])
        logger.info("Done...")
        return test_dataloader

    @time_func_wrapper(show_time=True)
    def create_object_localization_test_data(self, test_transformers: Callable,
                                             mask_transformers: Callable,
                                             exclude_names: List[Path]) -> DataLoader:
        logger.info("Loading test dataset with masks")
        images_path = Path(self.config['data_dir'])
        masks_path = Path(self.config['masks_dir'])

        # let's get all the files
        images_filename = img_utils.get_img_files(img_dir=images_path,
                                                  img_formats=['jpg', 'png', 'jpeg'],
                                                  with_batch_structure=self.config['with_batches'])

        logger.info(f"Number of train {self.config['class_0_name']} images {len(images_filename)}")

        # mask files for train
        mask_test_files = []
        test_files = []

        for filename in images_filename:

            if filename not in exclude_names:
                filename_ = str(filename).split("/")[-1]
                test_files.append(images_path / filename_)
                mask_test_files.append(masks_path / filename_)

        test_set = DatasetWithMasks.from_file_sources(imgs_filenames=test_files,
                                                      masks_filenames=mask_test_files,
                                                      labels=[1] * len(test_files),
                                                      mode=ModeEnum.TEST,
                                                      image_loader=img_utils.load_img,
                                                      mask_loader=img_utils.load_image_as_numpy,
                                                      on_load_transformers=test_transformers,
                                                      on_load_transformers_mask=mask_transformers)

        test_dataloader = torch.utils.data.DataLoader(test_set,
                                                      batch_size=self.config['batch_size'],
                                                      shuffle=self.config['shuffle'],
                                                      num_workers=self.config['num_workers'])

        return test_dataloader

    @time_func_wrapper(show_time=True)
    def create_few_shot_classifier_model_test_data(self, test_transformers: Callable) -> DataLoader:

        class_0_path = Path(self.config['data_dir']) / "test" / self.config["class_0_name"]
        class_1_path = Path(self.config['data_dir']) / "test" / self.config["class_1_name"]

        if str(class_0_path) == str(class_1_path):
            raise ValueError(f"Same path for {self.config['class_0_name']} and "
                             f" {self.config['class_1_name']} data")

        if self.config["data_type"] == "images":
            # let's get all the files
            test_class_0_data = img_utils.get_img_files(img_dir=class_0_path,
                                                        img_formats=['jpg', 'png', 'jpeg'],
                                                        with_batch_structure=self.config['with_batches']
                                                        )

            test_class_1_data = img_utils.get_img_files(img_dir=class_1_path,
                                                        img_formats=['jpg', 'png', 'jpeg'],
                                                        with_batch_structure=self.config['with_batches']
                                                        )

            if self.config['test_options']['max_test_size'] != 'all':
                logger.info(f"Limiting test data to size={self.config['test_options']['max_test_size']}")

                test_class_0_data = np.random.choice(test_class_0_data,
                                                     size=self.config['test_options']['max_test_size'],
                                                     replace=False).tolist()
                test_class_1_data = np.random.choice(test_class_1_data,
                                                     size=self.config['test_options']['max_test_size'],
                                                     replace=False).tolist()

            logger.info(f"Number of test {self.config['class_0_name']} images {len(test_class_0_data)}")
            logger.info(f"Number of test {self.config['class_1_name']} images {len(test_class_1_data)}")

        else:
            raise ValueError(f"Invalid data type={self.config['data_types']}")

        test_images = test_class_1_data + test_class_0_data
        labels = [1] * len(test_class_1_data) + [0] * len(test_class_0_data)

        logger.info(f"Train set size {len(test_images)}")

        # create the datasets
        test_set = ImagesDataset.from_file_sources(filenames=test_images,
                                                   labels=labels,
                                                   on_load_transformers=test_transformers)

        if self.config['test_options']['few_shot_options']['inference_with'] == 'with_prototypes':
            test_dataloader = torch.utils.data.DataLoader(test_set,
                                                          batch_size=self.config['batch_size'],
                                                          num_workers=self.config['num_workers'],
                                                          pin_memory=True)
        else:

            test_batch_sampler = TaskSampler(dataset=test_set,
                                             n_way=self.config['train_options']['n_classes'],
                                             n_shot=self.config['test_options']['few_shot_options'][
                                                 'n_support_pts'],
                                             n_query=self.config['test_options']['few_shot_options'][
                                                 'n_query_pts'],
                                             n_tasks=self.config['test_options']['few_shot_options'][
                                                 'n_iterations'])

            test_dataloader = torch.utils.data.DataLoader(test_set,
                                                          batch_sampler=test_batch_sampler,
                                                          num_workers=self.config['num_workers'],
                                                          pin_memory=True,
                                                          collate_fn=test_batch_sampler.episodic_collate_fn)
        logger.info("Done...")
        return test_dataloader

    @time_func_wrapper(show_time=True)
    def save_validation_train_files(self, trainer, train_info):

        save_as_pickle(trainer, filename=self.simulation_data_dir_output / "train_info.pkl")

        logger.info("Train info...")
        logger.info(train_info)

        logger.info(f"Best accuracy = {train_info.best_accuracy}")
        mlflow.log_param("best_accuracy", train_info.best_accuracy)

        # save the data
        train_loss = trainer.train_loss
        save_list_as_csv(train_loss,
                         filename=self.simulation_data_dir_output / self.config['train_options']['train_loss_file'])
        logger.info("Saved train loss")

        train_accuracy = trainer.train_acc
        save_list_as_csv(train_accuracy,
                         filename=self.simulation_data_dir_output / self.config['train_options']['train_accuracy_file'])
        logger.info("Saved train accuracy")

        validation_loss = trainer.val_loss
        save_list_as_csv(validation_loss,
                         filename=self.simulation_data_dir_output / self.config['validation_options']['val_loss_file'])
        logger.info("Saved validation loss")

        validation_accuracy = trainer.val_acc
        save_list_as_csv(validation_accuracy,
                         filename=self.simulation_data_dir_output / self.config['validation_options'][
                             'val_accuracy_file'])
        logger.info("Saved validation accuracy")
