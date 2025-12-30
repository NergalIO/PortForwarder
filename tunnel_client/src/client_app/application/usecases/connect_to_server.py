"""Connect to server use case."""

import logging
from typing import Optional

from ...interfaces.control_channel import IControlChannel
from ...domain.entities.tunnel_config import TunnelConfig
from ...common.errors import ConnectionError, AuthenticationError

logger = logging.getLogger(__name__)


class ConnectToServerUseCase:
    """Use case for connecting to the tunnel server."""
    
    def __init__(self, control_channel: IControlChannel):
        self._control_channel = control_channel
    
    async def execute(self, config: TunnelConfig) -> int:
        """
        Connect to server and register agent.
        
        Returns:
            Public port assigned by server
        
        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If authentication fails
        """
        try:
            # Connect to server
            await self._control_channel.connect(config.server_host, config.server_port)
            
            # Send HELLO
            await self._control_channel.send_hello(
                config.token, config.local_host, config.local_port
            )
            
            # Wait for WELCOME
            public_port = await self._control_channel.wait_for_welcome()
            
            logger.info(f"Connected to server, public port: {public_port}")
            return public_port
        
        except AuthenticationError:
            # Re-raise authentication errors without modification
            await self._control_channel.disconnect()
            raise
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            await self._control_channel.disconnect()
            raise ConnectionError(str(e))

