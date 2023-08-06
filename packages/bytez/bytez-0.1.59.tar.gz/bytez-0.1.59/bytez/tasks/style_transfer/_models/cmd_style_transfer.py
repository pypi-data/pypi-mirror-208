from typing import BinaryIO
from dataclasses import dataclass
from bytez.model import Model


@dataclass
class CmdStyleTransferModel(Model):
    def inference(self, image: BinaryIO) -> bytes:
        """
        Runs inference on the given image and returns the result as bytes.

        Args:
            image (BinaryIO): The binary image file to run inference on.

            test2 (bool, optional): The upscale factor for the output image. Defaults to 4.



        Returns:
            bytes: The result of the inference as bytes.
        """

        request_params = {
            'image': image,
        }

        url = 'https://cmd-styletransfer-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)
