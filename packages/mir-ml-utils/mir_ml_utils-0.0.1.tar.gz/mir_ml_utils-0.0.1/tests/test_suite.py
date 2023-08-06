"""module test_suite. Unit tests for
mir-engine

"""
import unittest

from tests.test_img_utils import TestImgUtils
from tests.test_prototypical_loss import TestPrototypicalLoss
from tests.test_pytorch_trainer import TestPyTorchTrainer
from tests.test_images_dataset import TestImagesDataset
from tests.test_math_ops import TestMathOps


def suite():

    suite = unittest.TestSuite()
    suite.addTest(TestImgUtils)
    suite.addTest(TestPrototypicalLoss)
    suite.addTest(TestPyTorchTrainer)
    suite.addTest(TestImagesDataset)
    suite.addTest(TestMathOps)
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
