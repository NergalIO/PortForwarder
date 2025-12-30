"""Tunnel configuration entity."""

from dataclasses import dataclass


@dataclass
class TunnelConfig:
    """Tunnel configuration."""
    
    server_host: str
    server_port: int
    token: str
    local_host: str
    local_port: int
    
    def validate(self) -> bool:
        """Validate the configuration."""
        if not self.server_host:
            return False
        if not (1 <= self.server_port <= 65535):
            return False
        if not self.token:
            return False
        if not self.local_host:
            return False
        if not (1 <= self.local_port <= 65535):
            return False
        return True

