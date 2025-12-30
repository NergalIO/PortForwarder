"""Asyncio-based control client implementation."""

import asyncio
import logging
from typing import Optional, Callable, Awaitable

from ...interfaces.control_channel import IControlChannel
from ...common.protocol import ProtocolCodec
from ...common.framing import WELCOME, OPEN, DATA, CLOSE

logger = logging.getLogger(__name__)


class AsyncioControlClient(IControlChannel):
    """Asyncio implementation of control channel."""
    
    def __init__(self):
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._codec = ProtocolCodec()
        self._message_handler: Optional[Callable[[int, int, bytes], Awaitable[None]]] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._welcome_future: Optional[asyncio.Future] = None
        self._welcome_received = False
    
    async def connect(self, host: str, port: int) -> None:
        """Connect to the server."""
        self._reader, self._writer = await asyncio.open_connection(host, port)
        logger.info(f"Connected to server {host}:{port}")
        
        # Create future for WELCOME message
        self._welcome_future = asyncio.Future()
        self._welcome_received = False
        
        # Start receiving messages (but don't process them until WELCOME is received)
        self._receive_task = asyncio.create_task(self._receive_loop())
    
    async def disconnect(self) -> None:
        """Disconnect from the server."""
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
        
        self._reader = None
        self._writer = None
        self._codec.clear()
        self._welcome_future = None
        self._welcome_received = False
        logger.info("Disconnected from server")
    
    async def send_hello(self, token: str, local_host: str, local_port: int) -> None:
        """Send HELLO message."""
        if not self._writer:
            raise RuntimeError("Not connected")
        
        msg = self._codec.encode_hello(token, local_host, local_port)
        self._writer.write(msg)
        await self._writer.drain()
        logger.debug("Sent HELLO message")
    
    async def wait_for_welcome(self) -> int:
        """Wait for WELCOME message and return public port."""
        if not self._welcome_future:
            raise RuntimeError("Not connected or WELCOME already received")
        
        # Wait for WELCOME to be received in receive loop
        try:
            public_port = await self._welcome_future
            return public_port
        except Exception as e:
            # If connection closed before WELCOME, it's likely authentication error
            if not self.is_connected():
                from ...common.errors import AuthenticationError
                raise AuthenticationError("Неверный токен")
            raise
    
    def set_message_handler(
        self, handler: Callable[[int, int, bytes], Awaitable[None]]
    ) -> None:
        """Set handler for incoming messages."""
        self._message_handler = handler
    
    async def send_data(self, conn_id: int, data: bytes) -> None:
        """Send DATA message."""
        if not self._writer:
            raise RuntimeError("Not connected")
        
        msg = self._codec.encode_data(conn_id, data)
        self._writer.write(msg)
        await self._writer.drain()
    
    async def send_close(self, conn_id: int) -> None:
        """Send CLOSE message."""
        if not self._writer:
            raise RuntimeError("Not connected")
        
        msg = self._codec.encode_close(conn_id)
        self._writer.write(msg)
        await self._writer.drain()
        logger.debug(f"Sent CLOSE for connection {conn_id}")
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._writer is not None and not self._writer.is_closing()
    
    async def _receive_loop(self) -> None:
        """Receive and process messages from server."""
        if not self._reader:
            return
        
        try:
            while True:
                data = await self._reader.read(4096)
                if not data:
                    # Connection closed - if WELCOME not received, it's likely auth error
                    if not self._welcome_received and self._welcome_future and not self._welcome_future.done():
                        from ...common.errors import AuthenticationError
                        self._welcome_future.set_exception(AuthenticationError("Неверный токен"))
                    break
                
                self._codec.feed(data)
                
                while True:
                    frame = self._codec.decode_frame()
                    if not frame:
                        break
                    
                    msg_type, conn_id, payload = frame
                    
                    # Handle WELCOME message first
                    if msg_type == WELCOME and not self._welcome_received:
                        public_port = self._codec.decode_welcome(payload)
                        logger.info(f"Received WELCOME, public port: {public_port}")
                        self._welcome_received = True
                        if self._welcome_future and not self._welcome_future.done():
                            self._welcome_future.set_result(public_port)
                        continue
                    
                    # Process other messages only after WELCOME is received
                    if self._welcome_received and self._message_handler:
                        try:
                            await self._message_handler(msg_type, conn_id, payload)
                        except Exception as e:
                            logger.error(f"Error in message handler: {e}", exc_info=True)
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # If error occurs before WELCOME, set exception on future
            if self._welcome_future and not self._welcome_future.done():
                # Check if connection was closed (likely authentication error)
                if not self.is_connected():
                    from ...common.errors import AuthenticationError
                    # Don't log authentication errors here - they will be handled upstream
                    self._welcome_future.set_exception(AuthenticationError("Неверный токен"))
                else:
                    logger.error(f"Error in receive loop: {e}", exc_info=True)
                    self._welcome_future.set_exception(e)
            else:
                logger.error(f"Error in receive loop: {e}", exc_info=True)

