"""module train_info. Dataclass that
wraps the return information from a fit method
of a trainer

"""
import json
import pickle
from typing import Any
from pathlib import Path
from dataclasses import dataclass, field


@dataclass(init=True, repr=True)
class TrainInfo(object):
    """Wrapper for training information

    """
    on_device_type: str = 'cpu'
    total_time: float = 0.0
    executed_epochs: int = 0
    best_accuracy: float = 0.0
    train_loss: list[float] = field(default_factory=list)
    train_accuracy: list[float] = field(default_factory=list)
    validate_loss: list[float] = field(default_factory=list)
    validate_accuracy: list[float] = field(default_factory=list)
    trainer_config: Any = None
