import unittest

import torch

from src.utils.math_ops import weighted_sum


class TestMathOps(unittest.TestCase):

    def test_weighted_sum(self):
        x = torch.ones(3)
        y = torch.ones(3)

        sum = weighted_sum(x, y, w=0.5)
        self.assertEqual(torch.sum(torch.eq(sum, torch.ones(3))), 3)


if __name__ == '__main__':
    unittest.main()
