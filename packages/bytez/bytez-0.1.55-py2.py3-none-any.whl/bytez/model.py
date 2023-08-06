from dataclasses import dataclass
import requests


@dataclass
class Model:
    # private, requires a mangled name
    def __inference(self, url: str, request_params: dict) -> bytes:
        files = request_params
        response = requests.post(url, files=files)

        if not response.ok:
            raise Exception(f'Request failed with {response.status_code}')

        return response.content
