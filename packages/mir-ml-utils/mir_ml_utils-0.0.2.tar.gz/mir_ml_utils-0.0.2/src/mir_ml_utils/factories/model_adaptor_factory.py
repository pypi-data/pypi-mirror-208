
from typing import Union

from mir_ml_utils.models.model_adaptor import AddFlattenLayerAdaptor, AddLinearLayerAdaptor, ComposedAdaptor, AdaptorBase
from mir_ml_utils.models.model_adaptor_type_enum import ModelAdaptorTypeEnum


def model_adaptor_builder(adaptor_type: Union[str | ModelAdaptorTypeEnum],
                          options: dict) -> Union[AdaptorBase | None]:

    if isinstance(adaptor_type, str):
        adaptor_type = ModelAdaptorTypeEnum.from_str(adaptor_type=adaptor_type)

    if adaptor_type == ModelAdaptorTypeEnum.LINEAR_LAYER_ADAPTOR:
        return AddLinearLayerAdaptor(params=options)
    elif adaptor_type == ModelAdaptorTypeEnum.FLATTEN_LAYER_ADAPTOR:
        return AddFlattenLayerAdaptor(params=options)
    elif adaptor_type == ModelAdaptorTypeEnum.COMPOSED_ADAPTOR:

        adaptors = []
        for adaptor in options:
            name = adaptor['name']
            options = adaptor['properties']
            adaptors.append(model_adaptor_builder(adaptor_type=name,
                                                  options=options))

        return ComposedAdaptor(params={'adaptors': adaptors})
    elif adaptor_type == ModelAdaptorTypeEnum.NONE:
        return None
    else:

        raise ValueError(f"Invalid adaptor_type={adaptor_type}")
