"""
Domain-specific exceptions for the analytics service.
"""


class InvalidLimitError(Exception):
    """Raised when a limit parameter is not a positive integer."""

    def __init__(self, limit: int):
        self.limit = limit
        super().__init__(f"Limit must be a positive integer, got: {limit}")
