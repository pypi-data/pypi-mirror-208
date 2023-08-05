import os
import re
from urllib.parse import urlparse

import requests

from bpkio_api import __version__
from bpkio_api.exceptions import BroadpeakIoHelperError

# Imports not used in the file, but necessary to ensure all handlers are loaded
from .dash import DASHHandler
from .generic import ContentHandler
from .hls import HLSHandler
from .jpeg import JPEGHandler
from .mp4 import MP4Handler
from .png import PNGHandler
from .vast import VASTHandler
from .vmap import VMAPHandler
from .xml import XMLHandler

# Registry for subclasses
_registry = {}

# Main headers
headers = {"User-Agent": f"bpkio-python-sdk/{__version__}"}


def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


for handler_cls in all_subclasses(ContentHandler):
    for content_type in handler_cls.content_types:
        _registry[content_type] = handler_cls
    for extension in handler_cls.file_extensions:
        _registry[extension] = handler_cls


def fetch_content_with_size_limit(url, size_limit, enforce_limit=True):
    response = requests.get(url, stream=True, headers=headers)
    content = b""
    for chunk in response.iter_content(chunk_size=1024):
        content += chunk
        if len(content) > size_limit:
            raise Exception("Content too long to be parseable efficiently")
    return content


def create_handler(url, get_full_content=False, from_url_only=False):
    try:
        content_type = ""
        if not from_url_only:
            response = requests.head(url, allow_redirects=True, headers=headers)
            content_type = response.headers.get("content-type")

        match = re.search(r"/(\.\w+)$", url)
        if match:
            # Special handling of Unified Streaming URLs
            file_extension = match.group(1)
        else:
            file_extension = os.path.splitext(urlparse(url).path)[1]

        handler_cls = _registry.get(content_type) or _registry.get(file_extension)

        content = None
        if handler_cls is None:
            if from_url_only:
                raise ValueError(
                    "No information available in the URL to determine content type: "
                    f"{content_type} / {file_extension}"
                )

            content = fetch_content_with_size_limit(
                url, 100 * 1024, enforce_limit=(not get_full_content)
            )

            # Fallback: analyze content if handler is not found by content-type
            # or file extension
            if content:
                for handler in all_subclasses(ContentHandler):
                    if handler.is_supported_content(content):
                        handler_cls = handler
                        break

        if handler_cls is None:
            raise ValueError(
                "Could not determine content type from content-type, file extension, or content of URL: "
                f"{content_type} / {file_extension}"
            )

        return handler_cls(url, content)

    except Exception as e:
        raise BroadpeakIoHelperError(
            status_code=400,
            message=f"Unable to determine a usable handler for url {url}",
            original_message=e.args[0]
            if len(e.args)
            else getattr(e, "description", None),
        )
