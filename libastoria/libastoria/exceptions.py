"""Exceptions."""


class AstoriaClientException(Exception):
    """An exception occurred with the Astoria client."""


class AstoriaDomainUnavailableException(Exception):
    """The requested domain was unavailable."""


class AstoriaRequestException(AstoriaClientException):
    """An error occurred during the request."""
