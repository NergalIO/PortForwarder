"""Agent session entity."""

from dataclasses import dataclass
from typing import Optional
import asyncio


@dataclass
class AgentSession:
    """Represents an active agent session."""
    
    agent_id: str
    token: str
    local_host: str
    local_port: int
    public_port: int
    control_writer: Optional[asyncio.StreamWriter] = None
    control_reader: Optional[asyncio.StreamReader] = None
    
    def __post_init__(self):
        """Initialize the session."""
        self._external_connections: dict[int, 'ExternalConn'] = {}
    
    def add_external_connection(self, conn: 'ExternalConn') -> None:
        """Add an external connection to this session."""
        self._external_connections[conn.conn_id] = conn
    
    def remove_external_connection(self, conn_id: int) -> None:
        """Remove an external connection from this session."""
        self._external_connections.pop(conn_id, None)
    
    def get_external_connection(self, conn_id: int) -> Optional['ExternalConn']:
        """Get an external connection by ID."""
        return self._external_connections.get(conn_id)
    
    def get_all_connections(self) -> list['ExternalConn']:
        """Get all external connections."""
        return list(self._external_connections.values())
    
    def has_connections(self) -> bool:
        """Check if there are any active external connections."""
        return len(self._external_connections) > 0

