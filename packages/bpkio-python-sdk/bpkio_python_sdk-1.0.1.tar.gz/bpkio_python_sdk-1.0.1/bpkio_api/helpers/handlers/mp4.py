from .generic import ContentHandler


class MP4Handler(ContentHandler):
    content_types = ["video/mp4"]
    file_extensions = [".mp4", ".mov"]

    def __init__(self, url, content):
        self.url = url
        self.content = content

    def read(self):
        return "Handling MP4 file."

    @staticmethod
    def is_supported_content(content):
        # TODO - add handling by trying to open the video (or at least the start of it)
        return False
