"""Asyncio-based control server implementation."""

import asyncio
import logging
from typing import Callable, Awaitable, Optional

from ...interfaces.control_server import IControlServer

logger = logging.getLogger(__name__)


class AsyncioControlServer(IControlServer):
    """Asyncio implementation of control server."""
    
    def __init__(self):
        self._server: Optional[asyncio.Server] = None
        self._connection_handler: Optional[Callable[[object, object], Awaitable[None]]] = None
    
    async def start(self, host: str, port: int) -> None:
        """Start the control server."""
        async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
            """Handle a new client connection."""
            if self._connection_handler:
                try:
                    await self._connection_handler(reader, writer)
                except Exception as e:
                    logger.error(f"Error handling control connection: {e}", exc_info=True)
                finally:
                    try:
                        writer.close()
                        await writer.wait_closed()
                    except Exception:
                        pass
        
        self._server = await asyncio.start_server(handle_client, host, port)
        logger.info(f"Control server listening on {host}:{port}")
    
    async def stop(self) -> None:
        """Stop the control server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("Control server stopped")
    
    def set_connection_handler(
        self, handler: Callable[[object, object], Awaitable[None]]
    ) -> None:
        """Set the handler for new connections."""
        self._connection_handler = handler

