from typing import BinaryIO
from bytez.model import Model


class HazyresearchH3Model(Model):
    def inference(self, input:str, d_model: int = 768, n_layer: int = 12, rotary_emb_dim = None, nheads: int = 12, genlen:int = 128, top_p:float = 0.9, top_k:int = 50) -> bytes:
        """
        Runs text generation on the given input string and returns the generated text as a string.

    Args:
      d_model (int, optional): The model dimension. Defaults to 768.
      n_layer (int, optional): The number of layers for the transformer. Defaults to 12.
      rotary_emb_dim (int, optional): For rotary embeddings. Set to None for default. Defaults to None.
      nheads (int, optional): The number of attention heads in the transformer. Defaults to 12.
      input (str): Input string for the model.
      genlen (int, optional): The length of the output string. Defaults to 128.
      top_p (float, optional): Top-p sampling value. Defaults to 0.9.
      top_k (int, optional): Top-k sampling value. Defaults to 50.

    Returns:
        str: The generated text.
        """

        request_params = {
    "input": input,
    "d_model": d_model,
    "n_layer": n_layer,
    "rotary_emb_dim": rotary_emb_dim,
    "nheads": nheads,
     "genlen": genlen,
    "top_p": top_p,
    "top_k": top_k
}

        url = 'https://hazyresearch-h3-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)