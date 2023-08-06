from .generic import ContentHandler


class PNGHandler(ContentHandler):
    content_types = ["image/png"]
    file_extensions = [".png"]

    def __init__(self, url, content):
        self.url = url
        self.content = content

    def read(self):
        return "Handling PNG file."

    @staticmethod
    def is_supported_content(content):
        # TODO - add handling by trying to open the image
        return False
