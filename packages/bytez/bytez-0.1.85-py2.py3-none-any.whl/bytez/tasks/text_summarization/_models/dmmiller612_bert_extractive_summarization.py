from typing import BinaryIO
from bytez.model import Model


class Dmmiller612BertExtractiveSummarizationModel(Model):
    def inference(self, input: str, min_length: int = 50, max_length: int = 100) -> bytes:
        """
        Summarizes text using the Summarizer model.

Args:
  input (str): The input text to be summarized.
  min_length (int, optional): The minimum length of the summary. Defaults to 50.
  max_length (int, optional): The maximum length of the summary. Defaults to 100.

Returns:
  BinaryIO: A binary file containing the summarized text.
        """

        request_params = {
   "input": "input",
   "min_length": "min_length",
   "max_length": "max_length"
}

        url = 'https://dmmiller612-bert-extractive-summarization-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)