from .generic import ContentHandler


class JPEGHandler(ContentHandler):
    content_types = ["image/jpeg"]
    file_extensions = [".jpg", ".jpeg"]

    def __init__(self, url, content):
        self.url = url
        self.content = content

    def read(self):
        return "Handling JPEG file."

    @staticmethod
    def is_supported_content(content):
        # TODO - add handling by trying to open the image
        return False
