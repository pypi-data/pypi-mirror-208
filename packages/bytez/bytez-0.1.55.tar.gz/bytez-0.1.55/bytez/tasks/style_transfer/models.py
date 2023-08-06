from dataclasses import dataclass
from bytez.tasks.style_transfer._models.cmd_style_transfer import CmdStyleTransferModel
from bytez.tasks.style_transfer._models.fast_style_transfer import FastStyleTransferModel
from bytez.tasks.style_transfer._models.tensorflow_fast_style import TensorFlowFastStyleTransferModel


@dataclass
class StyleTransferModels:
    fast_style_transfer = FastStyleTransferModel().inference
    cmd_style_transfer = CmdStyleTransferModel().inference
    tensorflow_fast_style = TensorFlowFastStyleTransferModel().inference
