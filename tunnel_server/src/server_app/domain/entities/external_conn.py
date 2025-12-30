"""External connection entity."""

from dataclasses import dataclass
from typing import Optional
import asyncio


@dataclass
class ExternalConn:
    """Represents an external client connection."""
    
    conn_id: int
    agent_id: str
    reader: Optional[asyncio.StreamReader] = None
    writer: Optional[asyncio.StreamWriter] = None
    
    def is_closed(self) -> bool:
        """Check if the connection is closed."""
        return self.writer is None or self.writer.is_closing()
    
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

