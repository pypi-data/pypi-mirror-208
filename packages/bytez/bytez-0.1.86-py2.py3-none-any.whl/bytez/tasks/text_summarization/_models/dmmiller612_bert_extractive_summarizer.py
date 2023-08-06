from typing import BinaryIO
from bytez.model import Model


class Dmmiller612BertExtractiveSummarizerModel(Model):
    def inference(self, input: str, num_sentences: int = 5, min_length: int = 0) -> bytes:
        """
        Summarizes input text into a shorter version that highlights the key points. 
    
                Args:
                    input (str): The text to be summarized.
                    
                    num_sentences (int, optional): The number of sentences for the resulting summary to have. Defaults to 5.
                    
                    min_length (int, optional): The minimum length (in characters) for each sentence in the summary. Defaults to 0.
                
                Returns:
                    str: The resulting summary as a string.
        """

        request_params = {
  "input": input,
  "num_sentences": num_sentences,
  "min_length": min_length
}

        url = 'https://dmmiller612-bert-extractive-summarizer-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)