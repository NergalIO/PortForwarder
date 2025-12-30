"""Common error classes for the tunnel client."""


class TunnelClientError(Exception):
    """Base exception for tunnel client errors."""
    pass


class ConnectionError(TunnelClientError):
    """Raised when connection fails."""
    pass


class ProtocolError(TunnelClientError):
    """Raised when protocol violation occurs."""
    pass


class AuthenticationError(TunnelClientError):
    """Raised when authentication fails."""
    pass

