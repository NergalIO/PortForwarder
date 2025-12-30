"""Common error classes for the tunnel server."""


class TunnelError(Exception):
    """Base exception for tunnel server errors."""
    pass


class AuthenticationError(TunnelError):
    """Raised when authentication fails."""
    pass


class PortAllocationError(TunnelError):
    """Raised when no ports are available for allocation."""
    pass


class ProtocolError(TunnelError):
    """Raised when protocol violation occurs."""
    pass


class ConnectionError(TunnelError):
    """Raised when connection-related error occurs."""
    pass

