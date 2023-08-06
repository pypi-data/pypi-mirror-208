from dataclasses import dataclass
from ._models.cmd_style_transfer import CmdStyleTransferModel
from ._models.fast_style_transfer import FastStyleTransferModel
from ._models.tensorflow_fast_style import TensorFlowFastStyleTransferModel


@dataclass
class StyleTransferModels:
    fast_style_transfer = FastStyleTransferModel().inference
    cmd_style_transfer = CmdStyleTransferModel().inference
    tensorflow_fast_style = TensorFlowFastStyleTransferModel().inference
