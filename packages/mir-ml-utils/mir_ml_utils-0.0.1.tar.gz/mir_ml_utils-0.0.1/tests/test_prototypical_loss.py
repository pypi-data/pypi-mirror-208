import unittest
import pytest
import torch

from src.loss_functions.distance_type import DistanceType
from src.loss_functions.prototypical_loss import PrototypicalLoss, PrototypicalLossConfig


class TestPrototypicalLoss(unittest.TestCase):

    def test_constructor_raises_invalid_DISTANCE(self):

        with pytest.raises(ValueError) as e:
            loss_config = PrototypicalLossConfig(distance_type=DistanceType.INVALID,
                                                 n_support_pts_per_cls=1)
            loss = PrototypicalLoss(loss_config)
            self.assertEqual(str(e), "distance type is INVALID")

    def test_constructor_raise_distance_is_None(self):
        with pytest.raises(ValueError) as e:
            loss_config = PrototypicalLossConfig(n_support_pts_per_cls=1)
            loss = PrototypicalLoss(loss_config)
            self.assertEqual(str(e), "distance type is None")
        
    def test_constructor_succeeds(self):
        loss_config = PrototypicalLossConfig(distance_type=DistanceType.L2_DISTANCE,
                                             n_support_pts_per_cls=1)
        loss = PrototypicalLoss(loss_config)
        self.assertEqual(loss.config.distance_type, DistanceType.L2_DISTANCE)

    @pytest.mark.skip("Fix the error with tensors")
    def test_loss(self):
        x = torch.ones(3, 3, 3)
        loss_config = PrototypicalLossConfig(distance_type=DistanceType.L2_DISTANCE,
                                             log_softmax_dim=0, n_support_pts_per_cls=1)
        loss = PrototypicalLoss(loss_config)
        loss.loss(input=x, target=x)


if __name__ == '__main__':
    unittest.main()
