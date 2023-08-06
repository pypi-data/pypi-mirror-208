from typing import BinaryIO
from bytez.model import Model


class HolmesAlanDsrvaeModel(Model):
    def inference(self, image: BinaryIO, upscale_factor: int = 4, testBatchSize: int = 64, gpu_mode: bool = True, chop_forward: bool = True,
                  patch_size: int = 128, stride: int = 8, threads: int = 6, seed: int = 123, gpus: int = 2) -> bytes:
        """
        Runs inference on the given image and returns the result as bytes.

        Args:
            image (BinaryIO): The binary image file to run inference on.

            upscale_factor (int, optional): The upscale factor for the output image. Defaults to 4.

            testBatchSize (int, optional): The batch size for inference. Defaults to 64.

            gpu_mode (bool, optional): Whether to run inference on GPU or not. Defaults to True.

            chop_forward (bool, optional): Whether to use forward-chop technique or not. Defaults to True.

            patch_size (int, optional): The patch size for inference. Defaults to 128.

            stride (int, optional): The stride size for inference. Defaults to 8.

            threads (int, optional): The number of threads to use for inference. Defaults to 6.

            seed (int, optional): The random seed for inference. Defaults to 123.

            gpus (int, optional): The number of GPUs to use for inference. Defaults to 2.

        Returns:
            bytes: The result of the inference as bytes.
        """

        request_params = {
            'image': image,
            'upscale_factor': upscale_factor,
            'testBatchSize': testBatchSize,
            'gpu_mode': gpu_mode,
            'chop_forward': chop_forward,
            'patch_size': patch_size,
            'stride': stride,
            'threads': threads,
            'seed': seed,
            'gpus': gpus,
        }

        url = 'https://holmes-alan-dsrvae-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)
