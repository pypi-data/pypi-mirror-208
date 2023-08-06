from typing import BinaryIO
from bytez.model import Model


class HolmesAlanDsrvaeModel(Model):
    def inference(self, image, upscale_factor=4, testBatchSize=64, gpu_mode=True, chop_forward_param=True, patch_size=128, stride=8, threads=6, seed=123, gpus=2, input_param='Test', model_type='VAE', output_param='Result', model_denoiser='./dSRVAE/models/VAE_denoiser.pth', model_SR='./dSRVAE/models/VAE_SR.pth') -> bytes:
        """
        Runs inference on an image and returns the result as a JPEG image bytes.

    Args:
      image (BinaryIO): The binary image file to run inference on.
      upscale_factor (int, optional): The upscale factor for the output image. Defaults to 4.
      testBatchSize (int, optional): The size of the test batch. Defaults to 64.
      gpu_mode (bool, optional): If the model will be run on a GPU. Defaults to True.
      chop_forward_param (bool, optional): Whether to perform chop_forward on the image. Defaults to True.
      patch_size (int, optional): Size of image patches. Defaults to 128.
      stride (int, optional): Patch stride size. Defaults to 8.
      threads (int, optional): Number of threads to use when loading images. Defaults to 6.
      seed (int, optional): Seed value for replication. Defaults to 123.
      gpus (int, optional): Number of GPUs to use. Defaults to 2.
      input_param (str, optional): Input parameter. Defaults to 'Test'.
      model_type (str, optional): Model type (VAE or other). Defaults to 'VAE'.
      output_param (str, optional): Desired output parameter. Defaults to 'Result'.
      model_denoiser (str, optional): Path to denoiser model. Defaults to './dSRVAE/models/VAE_denoiser.pth'.
      model_SR (str, optional): Path to super-resolution model. Defaults to './dSRVAE/models/VAE_SR.pth'.

    Returns:
        bytes: The resulting image in JPEG format as bytes.
        """

        request_params = {
    "image": image,
    "upscale_factor": upscale_factor,
    "testBatchSize": testBatchSize,
    "gpu_mode": gpu_mode,
    "chop_forward_param": chop_forward_param,
    "patch_size": patch_size,
    "stride": stride,
    "threads": threads,
    "seed": seed,
    "gpus": gpus,
    "input_param": input_param,
    "model_type": model_type,
    "output_param": output_param,
    "model_denoiser": model_denoiser,
    "model_SR": model_SR
}

        url = 'https://holmes-alan-dsrvae-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)