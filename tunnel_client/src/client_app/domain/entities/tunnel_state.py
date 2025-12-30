"""Tunnel state entity."""

from dataclasses import dataclass, field
from typing import Dict, Optional
import asyncio


@dataclass
class TunnelState:
    """Represents the current tunnel state."""
    
    connected: bool = False
    public_port: Optional[int] = None
    active_connections: Dict[int, 'LocalConnection'] = field(default_factory=dict)
    
    def add_connection(self, conn_id: int, connection: 'LocalConnection') -> None:
        """Add a local connection."""
        self.active_connections[conn_id] = connection
    
    def remove_connection(self, conn_id: int) -> None:
        """Remove a local connection."""
        self.active_connections.pop(conn_id, None)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)
    
    def clear(self) -> None:
        """Clear all state."""
        self.connected = False
        self.public_port = None
        self.active_connections.clear()


@dataclass
class LocalConnection:
    """Represents a local connection."""
    
    conn_id: int
    reader: Optional[asyncio.StreamReader] = None
    writer: Optional[asyncio.StreamWriter] = None
    
    async def close(self) -> None:
        """Close the connection."""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass
            self.writer = None
            self.reader = None

