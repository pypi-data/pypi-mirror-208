from typing import BinaryIO
from dataclasses import dataclass
import requests
from bytez.model import Model


@dataclass
class TensorFlowFastStyleTransferModel(Model):
    def inference(self, image: BinaryIO) -> bytes:
        """
        Runs inference on the given image and returns the result as bytes.

        Args:
            image (BinaryIO): The binary image file to run inference on.

        Returns:
            bytes: The result of the inference as bytes.
        """

        request_params = {
            'image': image,
        }

        url = 'https://tensorflow-fast-style-transfer-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)
