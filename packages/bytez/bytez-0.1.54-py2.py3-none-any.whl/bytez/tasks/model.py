from dataclasses import dataclass
from bytez.tasks.super_resolution import SuperResolutionModels
from bytez.tasks.style_transfer import StyleTransferModels


@dataclass
class Model:
    pass


# Add methods and properties from each model
for models in [SuperResolutionModels, StyleTransferModels]:
    for model_name in dir(models):
        model = getattr(models, model_name)

        if not hasattr(model, '__dict__'):  # Skip non-model attributes
            continue

        for attr_name in model.__dict__:
            attr = getattr(model, attr_name)
            if callable(attr) or isinstance(attr, property):
                setattr(Model, attr_name, attr)
