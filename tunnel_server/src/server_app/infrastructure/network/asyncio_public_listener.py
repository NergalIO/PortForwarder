"""Asyncio-based public listener implementation."""

import asyncio
import logging
from typing import Callable, Awaitable, Optional

from ...interfaces.public_listener_factory import IPublicListenerFactory

logger = logging.getLogger(__name__)


class AsyncioPublicListener:
    """Represents a public listener."""
    
    def __init__(self, server: asyncio.Server):
        self._server = server
    
    async def close(self) -> None:
        """Close the listener."""
        self._server.close()
        await self._server.wait_closed()


class AsyncioPublicListenerFactory(IPublicListenerFactory):
    """Factory for creating asyncio public listeners."""
    
    async def create_listener(
        self,
        port: int,
        connection_handler: Callable[[object, object], Awaitable[None]]
    ) -> AsyncioPublicListener:
        """Create a listener on the given port."""
        async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
            """Handle a new external client connection."""
            try:
                await connection_handler(reader, writer)
            except Exception as e:
                logger.error(f"Error handling external connection: {e}", exc_info=True)
            finally:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass
        
        server = await asyncio.start_server(handle_client, '0.0.0.0', port)
        logger.info(f"Public listener started on port {port}")
        return AsyncioPublicListener(server)

