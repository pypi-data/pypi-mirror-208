from dataclasses import dataclass
import requests


@dataclass
class Model:
    # private, requires a mangled name
    def __inference(self, url: str, request_params: dict) -> bytes:
        files = {}
        data = {}

        # automatically determine what the params are, if they should be files, they get put in as files
        # if they should be raw data, that's passed in as raw data
        for key, value in request_params.items():    
            # These are simply omitted from the form, if they aren't, then they are recast into strings
            if value is None:
                continue

            if hasattr(value, 'read') and callable(value.read):
                # Check if value is a file-like object
                files[key] = value
            else:
                # Convert non-file values to strings
                if not isinstance(value, str):
                    value = str(value)
                data[key] = value

        response = requests.post(url, files=files, data=data)

        if not response.ok:
            raise Exception(f'Request failed with {response.status_code}')

        return response.content
