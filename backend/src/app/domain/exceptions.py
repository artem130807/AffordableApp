class DomainError(Exception):
    """Base error safe to expose through the API."""


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class AuthenticationError(DomainError):
    pass


class RefreshTokenReuseError(AuthenticationError):
    """Signals that token-family revocation must be committed before returning 401."""


class PermissionDeniedError(DomainError):
    pass


class ValidationError(DomainError):
    pass


class ServiceUnavailableError(DomainError):
    pass
