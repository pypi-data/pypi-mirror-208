import requests
import mimetypes
import os
from io import BytesIO


class Attachment:
    def __init__(self, attachment_path):
        self.attachment_path = attachment_path

    def get_attachment(self) -> tuple:
        if self.attachment_path.startswith("http"):
            response = requests.get(self.attachment_path)
            content_type = response.headers.get("content-type")
            if content_type and ("image" not in content_type and "document" not in content_type):
                raise ValueError("URL does not point to an image")
            return os.path.basename(self.attachment_path), BytesIO(response.content).read(), mimetypes.guess_type(os.path.basename(self.attachment_path))
        elif os.path.isfile(self.attachment_path):
            with open(self.attachment_path, "rb") as f:
                return os.path.basename(self.attachment_path), f.read(), mimetypes.guess_type(os.path.basename(self.attachment_path))[0]
        else:
            raise ValueError("Invalid attachment path")
