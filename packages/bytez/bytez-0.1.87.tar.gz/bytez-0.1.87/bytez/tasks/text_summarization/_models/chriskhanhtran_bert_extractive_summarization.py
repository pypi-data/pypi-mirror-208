from typing import BinaryIO
from bytez.model import Model


class ChriskhanhtranBertExtractiveSummarizationModel(Model):
    def inference(self, input: str = '', max_length: int = 3) -> bytes:
        """
        Generates a summary of the input text using the BERT-based extractive summarization model.

Args:
  input (str, optional): The input text to summarize. Defaults to an empty string.
  max_length (int, optional): The maximum length of the output summary, in number of sentences. Defaults to 3.

Returns:
  str: The generated summary text.
        """

        request_params = {'input': input, 'max_length': max_length}

        url = 'https://chriskhanhtran-bert-extractive-summarization-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)