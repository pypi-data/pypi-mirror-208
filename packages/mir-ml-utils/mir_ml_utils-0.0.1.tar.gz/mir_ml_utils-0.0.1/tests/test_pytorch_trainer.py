"""unit tests for testing PyTorchTrainer

"""
import unittest
import pytest
from pathlib import Path
import torch.nn as nn
from torch.optim.adam import Adam

from src.trainers.pytorch_trainer import PyTorchTrainer
from src.trainers.pytorch_trainer import PyTorchTrainerConfig


class DummyModel(nn.Module):
    def __init__(self):
        super(DummyModel, self).__init__()
        self.linear = nn.Linear(28*28, 512)


class TestLoss(object):
    pass


class TestPyTorchTrainer(unittest.TestCase):

    """
    def setUp(self) -> None:
        self.trainer_config = PyTorchTrainerConfig(save_best_model=False)
        self.trainer_config.model = DummyModel()
        self.trainer_config.optimizer = Adam(self.trainer_config.model.parameters())
        self.trainer_config.loss_func = TestLoss()

    """

    def test_ctor_succeeds(self):
        trainer_config = PyTorchTrainerConfig(save_best_model=False)
        trainer_config.model = DummyModel()
        trainer_config.optimizer = Adam(trainer_config.model.parameters())
        trainer_config.loss_func = TestLoss()

        trainer = PyTorchTrainer(config=trainer_config)

    def test_ctor_fails_config_is_None(self):

        with pytest.raises(ValueError) as e:
            trainer = PyTorchTrainer(config=None)

            self.assertEqual(str(e), "Configuration object is None")

    def test_ctor_fails_model_is_None(self):

        with pytest.raises(ValueError) as e:
            trainer_config = PyTorchTrainerConfig()
            trainer = PyTorchTrainer(config=trainer_config)

            self.assertEqual(str(e), "Model is not None")

    def test_ctor_fails_optimizer_is_None(self):

        with pytest.raises(ValueError) as e:
            trainer_config = PyTorchTrainerConfig(model=DummyModel())
            trainer = PyTorchTrainer(config=trainer_config)

            self.assertEqual(str(e), "Optimizer is None")

    def test_ctor_fails_loss_func_is_None(self):

        with pytest.raises(ValueError) as e:
            trainer_config = PyTorchTrainerConfig()
            trainer_config.model = DummyModel()
            trainer_config.optimizer = Adam(trainer_config.model.parameters())
            trainer = PyTorchTrainer(config=trainer_config)

            self.assertEqual(str(e), "Loss function is None")

    def test_ctor_fails_invalid_number_of_epochs(self):

        with pytest.raises(ValueError) as e:
            trainer_config = PyTorchTrainerConfig()
            trainer_config.model = DummyModel()
            trainer_config.optimizer = Adam(trainer_config.model.parameters())
            trainer_config.loss_func = TestLoss()
            trainer_config.n_epochs = 0
            trainer = PyTorchTrainer(config=trainer_config)

            self.assertEqual(str(e), "Invalid number of epochs. n_epochs should be >=1")

    def test_fit_fails_train_data_None(self):
        trainer_config = PyTorchTrainerConfig(save_best_model=False)
        trainer_config.model = DummyModel()
        trainer_config.optimizer = Adam(trainer_config.model.parameters())
        trainer_config.loss_func = TestLoss()
        trainer = PyTorchTrainer(config=trainer_config)

        with pytest.raises(ValueError) as e:
            trainer.actions_before_train(train_data=None, validate_data=None)

            self.assertEqual(str(e), "train_data is None")

    """
    def test_fit_fails_best_model_path_invalid(self):
        self.trainer_config.save_best_model = True

        trainer = PyTorchTrainer(config=self.trainer_config)

        with pytest.raises(ValueError) as e:
            trainer.fit(train_data=None)
            self.trainer_config.save_best_model = False
            self.assertEqual(str(e), "Invalid Configuration, save_best_model is true but best_model_path is None")
    """

    """
    def test_fit_succeeds_valid_best_model_path(self):
        self.trainer_config.save_best_model = True
        self.trainer_config.best_model_path = Path("test_path")

        trainer = PyTorchTrainer(config=self.trainer_config)

        with pytest.raises(ValueError) as e:
            trainer.fit(train_data=None)
            self.trainer_config.save_best_model = False
            print(str(e))
            self.assertEqual(str(e), "train_data is None")
    """

    def test_fit_fails_invalid_config_empty_train_loss_path(self):
        trainer_config = PyTorchTrainerConfig(save_best_model=False)
        trainer_config.model = DummyModel()
        trainer_config.optimizer = Adam(trainer_config.model.parameters())
        trainer_config.loss_func = TestLoss()

        trainer_config.save_best_model = True
        trainer_config.best_model_path = Path("test_path")
        trainer_config.save_training_loss_info = True
        trainer_config.training_loss_path = None

        trainer = PyTorchTrainer(config=trainer_config)

        with pytest.raises(ValueError) as e:
            trainer.actions_before_train(train_data={}, validate_data=None)
            self.assertEqual(str(e),
                             "Requested to save the training info but the specified path  is None")

    def test_fit_fails_invalid_config_empty_validation_loss_path(self):
        trainer_config = PyTorchTrainerConfig(save_best_model=False)
        trainer_config.model = DummyModel()
        trainer_config.optimizer = Adam(trainer_config.model.parameters())
        trainer_config.loss_func = TestLoss()

        trainer_config.save_best_model = True
        trainer_config.best_model_path = Path("test_path")
        trainer_config.save_training_loss_info = False
        trainer_config.training_loss_path = None
        trainer_config.save_validation_loss_info = True
        trainer_config.validate_loss_path = None

        trainer = PyTorchTrainer(config=trainer_config)

        with pytest.raises(ValueError) as e:
            trainer.actions_before_train(train_data={}, validate_data=None)
            self.assertEqual(str(e),
                             "Requested to save the validation info but the specified path  is None")


if __name__ == '__main__':
    unittest.main()
