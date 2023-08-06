import json
from typing import BinaryIO
from dataclasses import dataclass
import requests
import pkg_resources

data = pkg_resources.resource_string('bytez', 'data/tasks.json')

tasks = json.loads(data)


@dataclass
class Handler:
    url: str

    def inference(self, input_img: BinaryIO) -> bytes:
        files = {'image': input_img}
        response = requests.post(self.url, files=files)

        # reset seek index to start of file
        input_img.seek(0)

        if not response.ok:
            raise Exception(f'Request failed with {response.status_code}')

        return response.content

# TODO use enums to accomplish this


def pipeline(task,
             model) -> Handler:
    task = tasks.get(task)

    if not task:
        raise Exception(f"{task} is not supported by this package.")

    url = task.get(model)

    if not url:
        raise Exception(f"{model} is not supported by this package.")

    return Handler(url=url)
