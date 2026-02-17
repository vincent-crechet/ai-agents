"""
Domain-specific exceptions for the url-management service.

These exceptions are raised by the service layer and mapped to HTTP status
codes by the API layer.
"""


class UrlNotFoundError(Exception):
    """Raised when a short code does not exist in the repository."""

    def __init__(self, short_code: str):
        self.short_code = short_code
        super().__init__(f"Short URL not found: {short_code}")


class InvalidUrlError(Exception):
    """Raised when a URL fails validation."""

    def __init__(self, url: str, reason: str = "Invalid URL format"):
        self.url = url
        self.reason = reason
        super().__init__(f"Invalid URL: {url} - {reason}")
