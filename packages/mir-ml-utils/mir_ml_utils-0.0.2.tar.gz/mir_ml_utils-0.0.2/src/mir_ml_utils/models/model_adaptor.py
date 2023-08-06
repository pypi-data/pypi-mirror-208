import torch.nn as nn


class AdaptorBase(object):

    def __init__(self, params: dict):
        self.params = params

    def __call__(self, model_ft: nn.Module) -> nn.Module:
        return model_ft


class AddLinearLayerAdaptor(AdaptorBase):

    def __init__(self, params: dict):
        super(AddLinearLayerAdaptor, self).__init__(params=params)

    def add_linear_layer(self, model_ft: nn.Module) -> nn.Module:
        num_ftrs = model_ft.fc.in_features
        if self.params['out'] == 'LAST_LAYER':
            model_ft.fc = nn.Linear(num_ftrs, num_ftrs)
        else:
            model_ft.fc = nn.Linear(num_ftrs, self.params['out'])
        return model_ft

    def __call__(self, model_ft: nn.Module) -> nn.Module:
        return self.add_linear_layer(model_ft=model_ft)


class AddFlattenLayerAdaptor(AdaptorBase):

    def __init__(self, params: dict={}):
        super(AddFlattenLayerAdaptor, self).__init__(params=params)

    def __call__(self, model_ft: nn.Module) -> nn.Module:
        model_ft.fc = nn.Flatten()
        return model_ft


class ComposedAdaptor(AdaptorBase):

    def __init__(self, params: dict):
        super(ComposedAdaptor, self).__init__(params=params)

    def __call__(self, model_ft: nn.Module) -> nn.Module:

        for adaptor in self.params['adaptors']:
            model_ft = adaptor(model_ft)
        return model_ft


