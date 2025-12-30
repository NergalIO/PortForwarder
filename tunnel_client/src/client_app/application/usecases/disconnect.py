"""Disconnect use case."""

import logging
from typing import Dict

from ...interfaces.control_channel import IControlChannel
from ...domain.entities.tunnel_state import TunnelState, LocalConnection

logger = logging.getLogger(__name__)


class DisconnectUseCase:
    """Use case for disconnecting from the server."""
    
    def __init__(self, control_channel: IControlChannel, tunnel_state: TunnelState):
        self._control_channel = control_channel
        self._tunnel_state = tunnel_state
    
    async def execute(self) -> None:
        """Disconnect from server and close all connections."""
        # Close all local connections
        connections = list(self._tunnel_state.active_connections.values())
        for conn in connections:
            await conn.close()
        
        self._tunnel_state.active_connections.clear()
        
        # Disconnect control channel
        await self._control_channel.disconnect()
        
        # Clear state
        self._tunnel_state.clear()
        
        # Reset statistics
        if hasattr(self._tunnel_state, '_bytes_sent'):
            self._tunnel_state._bytes_sent = 0
        if hasattr(self._tunnel_state, '_bytes_received'):
            self._tunnel_state._bytes_received = 0
        
        logger.info("Disconnected from server")

