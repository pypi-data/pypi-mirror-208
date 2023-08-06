"""module loss_wrapper. Wrapper that holds the result
of loss functions

"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(init=True, repr=True)
class LossFuncResult(object):
    loss: Any = None
    accuracy: Any = None

    def save(self, filename: Path) -> None:
        raise NotImplementedError("This function is not implemented")