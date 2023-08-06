import logging
from abc import ABC, abstractmethod
from typing import Dict, List
from urllib.parse import parse_qs, urlparse

import requests

from bpkio_api import __version__

headers = {"User-Agent": f"bpkio-python-sdk/{__version__}"}


class ContentHandler(ABC):
    content_types = []
    file_extensions = []

    document = None

    @abstractmethod
    def __init__(self, url, content: bytes | None = None):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.url = url
        self.original_url = url
        if content:
            self._content = content
        else:
            self._content = None

        # broadpeak session id (in case handler is for a bpk sessionservice)
        self.session_id = None

    @property
    def content(self):
        if self._content is None:
            self._fetch_content()
        return self._content

    def _fetch_content(self) -> bytes:
        self.logger.debug(f"Fetching content from {self.url}")
        response = requests.get(self.url, headers=headers)
        self._content = response.content

        # overwrite the URL, in case of redirect
        self.url = response.url

        # check if a broadpeak.io session was started
        params = parse_qs(
            urlparse(self.url).query, keep_blank_values=True, strict_parsing=False
        )
        if "sessionid" in params:
            self.session_id = params["sessionid"][0]

        return self._content

    def reload(self):
        self._fetch_content()

    @staticmethod
    @abstractmethod
    def is_supported_content(content) -> bool:
        pass

    def has_children(self) -> bool:
        return False

    def get_child(self, index: int) -> "ContentHandler | None":
        return None

    @abstractmethod
    def read(self):
        pass

    def extract_info(self) -> Dict | None:
        return None

    def extract_features(self) -> List[Dict] | None:
        return None
