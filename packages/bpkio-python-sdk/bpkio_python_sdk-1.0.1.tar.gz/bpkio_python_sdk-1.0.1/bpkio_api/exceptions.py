class BroadpeakIoApiError(Exception):
    def __init__(self, status_code, message, reason, url):
        self.status_code = status_code
        self.message = message
        self.reason = reason
        self.url = url
        super().__init__(message)


class AccessForbiddenError(BroadpeakIoApiError):
    def __init__(self, status_code, message, reason, url):
        super().__init__(status_code, message, reason, url)


class ResourceExistsError(BroadpeakIoApiError):
    def __init__(self, status_code, message, reason, url):
        super().__init__(status_code, message, reason, url)


class BroadpeakIoHelperError(Exception):
    def __init__(self, status_code, message, original_message):
        self.status_code = status_code
        self.message = message
        self.original_message = original_message
        super().__init__(message)


class InvalidApiKeyFormat(BroadpeakIoApiError):
    def __init__(self, reason):
        super().__init__(
            403, "The API Key provided has an invalid format", reason, None
        )
