import logging

import bpkio_api.helpers.handlers as handlers
from bpkio_api.exceptions import BroadpeakIoHelperError
from bpkio_api.models.Sources import SourceType

logger = logging.getLogger(__name__)


class SourceTypeDetector:
    @staticmethod
    def determine_source_type(url) -> SourceType:
        handler = handlers.factory.create_handler(url)

        match handler:
            case handlers.HLSHandler() | handlers.DASHHandler():
                if handler.is_live():
                    return SourceType.LIVE
                else:
                    return SourceType.ASSET

            case handlers.JPEGHandler() | handlers.PNGHandler() | handlers.MP4Handler():
                return SourceType.SLATE

            case handlers.VASTHandler() | handlers.VMAPHandler():
                return SourceType.AD_SERVER

            case _:
                raise BroadpeakIoHelperError(
                    status_code=404,
                    message=f"Unsupported document type for source at {url}",
                    original_message=None,
                )
