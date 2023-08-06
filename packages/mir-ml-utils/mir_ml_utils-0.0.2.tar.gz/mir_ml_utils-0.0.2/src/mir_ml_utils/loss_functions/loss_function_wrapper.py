from typing import Any
from typing import Callable

from .loss_function_result import LossFuncResult


class LossFunctionWrapper(object):

    def __init__(self, loss: Callable):
        self.loss = loss

    def __call__(self, *args, **kwargs) -> Any:
        result = LossFuncResult(loss=self.loss(*args), accuracy=None)
        return result