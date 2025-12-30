"""Start tunnel use case."""

import asyncio
import logging
from typing import Optional

from ...interfaces.control_channel import IControlChannel
from ...interfaces.local_transport import ILocalTransport
from ...domain.entities.tunnel_state import TunnelState, LocalConnection
from ...common.protocol import ProtocolCodec
from ...common.framing import OPEN, DATA, CLOSE

logger = logging.getLogger(__name__)


class StartTunnelUseCase:
    """Use case for starting tunnel operations."""
    
    def __init__(
        self,
        control_channel: IControlChannel,
        local_transport: ILocalTransport,
        tunnel_state: TunnelState,
        codec: ProtocolCodec
    ):
        self._control_channel = control_channel
        self._local_transport = local_transport
        self._tunnel_state = tunnel_state
        self._codec = codec
        
        # Initialize statistics
        self._tunnel_state._bytes_sent = 0
        self._tunnel_state._bytes_received = 0
        
        # Setup message handler
        self._control_channel.set_message_handler(self._handle_message)
    
    async def _handle_message(self, msg_type: int, conn_id: int, payload: bytes) -> None:
        """Handle incoming message from server."""
        if msg_type == OPEN:
            await self._handle_open(conn_id)
        elif msg_type == DATA:
            await self._handle_data(conn_id, payload)
        elif msg_type == CLOSE:
            await self._handle_close(conn_id)
        else:
            logger.warning(f"Unknown message type: {msg_type}")
    
    async def _handle_open(self, conn_id: int) -> None:
        """Handle OPEN message - connect to local service."""
        if conn_id in self._tunnel_state.active_connections:
            logger.warning(f"Connection {conn_id} already exists")
            return
        
        # Get local config from state (we'll need to store it)
        local_host = getattr(self._tunnel_state, '_local_host', 'localhost')
        local_port = getattr(self._tunnel_state, '_local_port', 8080)
        
        try:
            # Connect to local service
            reader, writer = await self._local_transport.connect(local_host, local_port)
            
            # Create connection
            conn = LocalConnection(conn_id=conn_id, reader=reader, writer=writer)
            self._tunnel_state.add_connection(conn_id, conn)
            
            # Start relaying data
            asyncio.create_task(self._relay_local_to_server(conn))
            
            logger.info(f"Opened connection {conn_id} to local service")
        
        except Exception as e:
            logger.error(f"Failed to connect to local service: {e}")
            # Send CLOSE to server
            await self._control_channel.send_close(conn_id)
    
    async def _handle_data(self, conn_id: int, payload: bytes) -> None:
        """Handle DATA message - relay to local service."""
        conn = self._tunnel_state.active_connections.get(conn_id)
        if not conn or not conn.writer:
            logger.warning(f"Connection {conn_id} not found or closed")
            return
        
        try:
            conn.writer.write(payload)
            await conn.writer.drain()
            # Update received bytes statistics
            self._tunnel_state._bytes_received += len(payload)
        except Exception as e:
            logger.error(f"Failed to write to local service: {e}")
            await self._close_connection(conn_id)
    
    async def _handle_close(self, conn_id: int) -> None:
        """Handle CLOSE message - close local connection."""
        await self._close_connection(conn_id)
    
    async def _close_connection(self, conn_id: int) -> None:
        """Close a connection."""
        conn = self._tunnel_state.active_connections.get(conn_id)
        if conn:
            await conn.close()
            self._tunnel_state.remove_connection(conn_id)
            logger.info(f"Closed connection {conn_id}")
    
    async def _relay_local_to_server(self, conn: LocalConnection) -> None:
        """Relay data from local service to server."""
        try:
            while True:
                if not conn.reader:
                    break
                
                data = await conn.reader.read(4096)
                if not data:
                    break
                
                await self._control_channel.send_data(conn.conn_id, data)
                # Update sent bytes statistics
                self._tunnel_state._bytes_sent += len(data)
        
        except Exception as e:
            logger.debug(f"Local->Server relay ended: {e}")
        finally:
            # Close connection
            await self._close_connection(conn.conn_id)
            # Notify server
            await self._control_channel.send_close(conn.conn_id)
    
    def set_local_config(self, local_host: str, local_port: int) -> None:
        """Set local service configuration."""
        self._tunnel_state._local_host = local_host
        self._tunnel_state._local_port = local_port

