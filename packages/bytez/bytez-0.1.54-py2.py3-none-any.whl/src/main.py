from typing import BinaryIO
from dataclasses import dataclass
import requests
import cv2
import numpy as np


# this will get more sophisticated as far as configuration goes, we'll want to abtract these into classes and leverage inheritance for various config options
tasks = {
    "style-transfer": {
        "fast-style-transfer": "https://fast-style-transfer-tfhmsoxnpq-uc.a.run.app",
        "cmd_styletransfer": "https://fast-style-transfer-tfhmsoxnpq-uc.a.run.app"
    }
}


@dataclass
class Handler:
    url: str

    def inference(self, input_img: BinaryIO) -> bytes:
        files = {'image': input_img}
        response = requests.post(self.url, files=files)

        if not response.ok:
            raise Exception(f'Request failed with {response.status_code}')

        return response.content

    @staticmethod
    def show_image(image: bytes):
        image_np = np.frombuffer(image, dtype=np.uint8)

        # then you can use the 'imdecode' function to decode the image
        image_cv = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        # create a window and display the image
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.imshow('image', image_cv)
        cv2.waitKey(0)


def pipeline(task, model) -> Handler:
    task = tasks.get(task)

    if not task:
        raise Exception(f"{task} is not supported by this package.")

    url = task.get(model)

    if not url:
        raise Exception(f"{model} is not supported by this package.")

    return Handler(url=url)


if __name__ == "__main__":
    with open('cat.jpg', 'rb') as file:

        style_transfer_runner = pipeline(
            task="style-transfer", model="fast-style-transfer")

        image = style_transfer_runner.inference(input_img=file)

        style_transfer_runner.show_image(image=image)
