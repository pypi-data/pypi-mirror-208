from typing import Any
import torch.optim as optim
from torch.optim import Adam, SGD

VALID_OPTIMIZER_NAMES = ["Adams", "SGD"]


def build_optimizer(model_params: Any, config) -> optim.Optimizer:
    optimizer_name = config['name']
    if optimizer_name == 'Adams':
        return Adam(model_params,
                    lr=config['learning_rate'],
                    weight_decay=config['weight_decay'])
    elif optimizer_name == 'SGD':
        return SGD(model_params,
                   lr=config['learning_rate'],
                   weight_decay=config['weight_decay'],
                   momentum=config['momentum'])

    raise ValueError(f"Name={optimizer_name} not in {VALID_OPTIMIZER_NAMES}")
