from abc import abstractmethod

from lxml import etree

from .generic import ContentHandler


class XMLHandler(ContentHandler):
    content_types = []
    file_extensions = []

    uri_attributes = []
    uri_elements = []

    def __init__(self, url, content: bytes | None = None):
        super().__init__(url, content)

    def read(self):
        return "Handling XML file."

    @staticmethod
    def is_supported_content(content) -> bool:
        return False

    @property
    @abstractmethod
    def xml_document(self) -> etree._Element:
        pass
