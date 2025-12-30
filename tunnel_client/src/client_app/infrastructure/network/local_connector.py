"""Local connector implementation."""

import asyncio
import logging
from typing import Tuple

from ...interfaces.local_transport import ILocalTransport

logger = logging.getLogger(__name__)


class AsyncioLocalConnector(ILocalTransport):
    """Asyncio implementation of local transport."""
    
    async def connect(self, host: str, port: int) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Connect to local service."""
        reader, writer = await asyncio.open_connection(host, port)
        logger.debug(f"Connected to local service {host}:{port}")
        return reader, writer

