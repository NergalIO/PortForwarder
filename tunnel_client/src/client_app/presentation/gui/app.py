"""Main GUI application."""

import customtkinter as ctk
import logging

from .views.connect_view import ConnectView
from .views.status_view import StatusView
from .views.logs_view import LogsView
from ..viewmodels.connection_vm import ConnectionViewModel
from ..gui.controllers.ui_controller import UIController
from ...infrastructure.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class TunnelClientApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self, event_bridge, connect_callback, disconnect_callback):
        super().__init__()
        
        self._event_bridge = event_bridge
        self._connect_callback = connect_callback
        self._disconnect_callback = disconnect_callback
        
        # View model
        self._view_model = ConnectionViewModel()
        self._view_model.set_state_changed_callback(self._on_state_changed)
        
        # Controller
        self._controller = UIController(self._view_model)
        
        # Config manager
        self._config_manager = ConfigManager()
        
        # Setup UI
        self._setup_ui()
        
        # Load saved configuration
        self._load_config()
        
        # Start event polling
        self._event_bridge.start_polling(self, 100)
    
    def _setup_ui(self) -> None:
        """Setup the UI."""
        self.title("Tunnel Client")
        self.geometry("800x600")
        
        # Create views
        self._connect_view = ConnectView(
            self,
            on_connect=self._on_connect_clicked,
            on_disconnect=self._on_disconnect_clicked
        )
        self._connect_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self._status_view = StatusView(self)
        self._status_view.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self._logs_view = LogsView(self)
        self._logs_view.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
    
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        config_dict = self._connect_view.get_config()
        if not config_dict:
            logger.error("Invalid configuration")
            return
        
        # Save configuration
        self._config_manager.save_config(config_dict)
        
        config = self._controller.on_connect_requested(config_dict)
        if config:
            self._connect_callback(config)
    
    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click."""
        self._controller.on_disconnect_requested()
        self._disconnect_callback()
    
    def _on_state_changed(self) -> None:
        """Handle state change in view model."""
        # Update UI based on view model
        self._connect_view.set_connected(self._view_model.connected)
        self._status_view.update_status(
            self._view_model.connected,
            self._view_model.public_port,
            self._view_model.active_connections
        )
        self._status_view.update_statistics(
            self._view_model.bytes_sent,
            self._view_model.bytes_received,
            self._view_model.send_speed,
            self._view_model.receive_speed
        )
    
    def handle_event(self, event_type: str, data) -> None:
        """Handle event from asyncio thread."""
        if event_type == "connected":
            self._controller.update_connection_status(True, data.get('public_port'))
        elif event_type == "disconnected":
            self._controller.update_connection_status(False)
            self._view_model.reset_statistics()
        elif event_type == "connection_error":
            # Show error message in logs
            error_msg = data.get('message', 'Ошибка подключения')
            logger.error(error_msg)
        elif event_type == "connections_changed":
            self._controller.update_active_connections(data.get('count', 0))
        elif event_type == "statistics_updated":
            self._view_model.update_statistics(
                data.get('bytes_sent', 0),
                data.get('bytes_received', 0),
                data.get('send_speed', 0.0),
                data.get('receive_speed', 0.0)
            )
    
    def _load_config(self) -> None:
        """Load saved configuration."""
        config = self._config_manager.load_config()
        if config:
            self._connect_view.set_config(config)

