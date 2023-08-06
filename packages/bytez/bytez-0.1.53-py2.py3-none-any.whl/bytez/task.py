from dataclasses import dataclass
from bytez.tasks.super_resolution import SuperResolutionModels
from bytez.tasks.style_transfer import StyleTransferModels


@dataclass
class Task:
    super_resolution = SuperResolutionModels
    style_transfer = StyleTransferModels


task = Task


# only export "task" from this module
__all__ = ['task']
