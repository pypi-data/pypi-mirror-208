import torch.nn as nn

VALID_LOSS_FUNCTION_NAMES = ["CrossEntropy"]


def build_loss_function(config):
    function_name = config['name']
    if function_name == 'CrossEntropy':
        return nn.CrossEntropyLoss()

    raise ValueError(f"Name={function_name} not in {VALID_LOSS_FUNCTION_NAMES}")