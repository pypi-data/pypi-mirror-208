import json
import logging

import bpkio_api.exceptions as errors

logger = logging.getLogger("bpkio_api.response_handler")


def raise_for_status(response):
    """Checks whether or not the response was successful."""

    logger.debug(response.request.method + " " + response.request.url)
    logger.debug(f" ({response.status_code}) -> {response.text}")

    if 200 <= response.status_code < 300:
        # Pass through the response.
        return response

    if response.status_code >= 500:
        raise errors.BroadpeakIoApiError(
            url=response.url,
            status_code=response.status_code,
            message=response.text,
            reason=response.reason,
        )

    response_payload = json.loads(response.text)

    if response.status_code == 403:
        if "existing" in response_payload["message"]:
            raise errors.ResourceExistsError(
                url=response.url,
                status_code=response.status_code,
                message=response_payload["message"],
                reason=response.reason,
            )

        raise errors.AccessForbiddenError(
            url=response.url,
            status_code=response.status_code,
            message=response_payload["message"],
            reason=response.reason,
        )
    else:
        raise errors.BroadpeakIoApiError(
            url=response.url,
            status_code=response.status_code,
            message=response_payload["message"],
            reason=response.reason,
        )


def return_count(response):
    return int(response.headers["x-pagination-total-count"])
