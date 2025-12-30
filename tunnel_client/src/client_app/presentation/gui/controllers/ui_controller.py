"""UI controller."""

import logging
from typing import Optional

from ...viewmodels.connection_vm import ConnectionViewModel
from ....domain.entities.tunnel_config import TunnelConfig

logger = logging.getLogger(__name__)


class UIController:
    """Controller for UI events."""
    
    def __init__(self, view_model: ConnectionViewModel):
        self._view_model = view_model
    
    def on_connect_requested(self, config_dict: dict) -> Optional[TunnelConfig]:
        """Handle connect request from UI."""
        try:
            config = TunnelConfig(
                server_host=config_dict['server_host'],
                server_port=config_dict['server_port'],
                token=config_dict['token'],
                local_host=config_dict['local_host'],
                local_port=config_dict['local_port']
            )
            
            if not config.validate():
                logger.error("Invalid configuration")
                return None
            
            return config
        
        except Exception as e:
            logger.error(f"Error creating config: {e}")
            return None
    
    def on_disconnect_requested(self) -> None:
        """Handle disconnect request from UI."""
        logger.info("Disconnect requested")
    
    def update_connection_status(self, connected: bool, public_port: Optional[int] = None) -> None:
        """Update connection status in view model."""
        self._view_model.update_connection_status(connected, public_port)
    
    def update_active_connections(self, count: int) -> None:
        """Update active connections count in view model."""
        self._view_model.update_active_connections(count)

