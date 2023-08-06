from dataclasses import dataclass
from bytez.tasks.super_resolution._models.dsrvae import HolmesAlanDsrvaeModel


@dataclass
class SuperResolutionModels:
    holmes_alan_dsrvae = HolmesAlanDsrvaeModel().inference
