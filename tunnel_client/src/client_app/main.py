"""Main entry point for tunnel client."""

import asyncio
import logging
import threading
import sys
from pathlib import Path
from typing import Optional

import customtkinter as ctk

# Add src directory to path for direct execution
# This allows running the script directly: python main.py
_file_path = Path(__file__).resolve()
_src_path = _file_path.parent.parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Use absolute imports after adding src to path
from client_app.infrastructure.logging.logging_adapter import setup_logging
from client_app.infrastructure.network.asyncio_control_client import AsyncioControlClient
from client_app.infrastructure.network.local_connector import AsyncioLocalConnector
from client_app.application.usecases.connect_to_server import ConnectToServerUseCase
from client_app.application.usecases.disconnect import DisconnectUseCase
from client_app.common.errors import AuthenticationError
from client_app.application.usecases.start_tunnel import StartTunnelUseCase
from client_app.domain.entities.tunnel_config import TunnelConfig
from client_app.domain.entities.tunnel_state import TunnelState
from client_app.common.protocol import ProtocolCodec
from client_app.common.threading_bridge import ThreadingBridge
from client_app.presentation.gui.app import TunnelClientApp

logger = logging.getLogger(__name__)


class TunnelClient:
    """Main tunnel client application."""
    
    def __init__(self):
        # Infrastructure
        self._control_channel = AsyncioControlClient()
        self._local_transport = AsyncioLocalConnector()
        self._codec = ProtocolCodec()
        
        # Domain
        self._tunnel_state = TunnelState()
        
        # Use cases
        self._connect_uc = ConnectToServerUseCase(self._control_channel)
        self._disconnect_uc = DisconnectUseCase(self._control_channel, self._tunnel_state)
        self._start_tunnel_uc = StartTunnelUseCase(
            self._control_channel, self._local_transport, self._tunnel_state, self._codec
        )
        
        # Event bridge
        self._event_bridge = ThreadingBridge(self._handle_gui_event)
        
        # Asyncio loop
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_thread: Optional[threading.Thread] = None
    
    def _handle_gui_event(self, event_type: str, data) -> None:
        """Handle event in GUI thread (called from bridge)."""
        # This will be called from the GUI thread via root.after
        # The app will handle it
        pass
    
    def start_gui(self) -> None:
        """Start the GUI."""
        # Setup asyncio loop in separate thread
        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()
        
        self._loop_thread = threading.Thread(target=run_loop, daemon=True)
        self._loop_thread.start()
        
        # Wait for loop to be ready
        while self._loop is None:
            threading.Event().wait(0.1)
        
        # Create GUI
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        app = TunnelClientApp(
            self._event_bridge,
            self._on_connect_requested,
            self._on_disconnect_requested
        )
        
        # Store app reference for event handling
        self._app = app
        
        # Update event bridge callback
        self._event_bridge._gui_callback = app.handle_event
        
        # Start GUI
        app.mainloop()
    
    def _on_connect_requested(self, config: TunnelConfig) -> None:
        """Handle connect request from GUI."""
        def connect_async():
            async def do_connect():
                try:
                    # Set local config
                    self._start_tunnel_uc.set_local_config(config.local_host, config.local_port)
                    
                    # Connect
                    public_port = await self._connect_uc.execute(config)
                    
                    # Update state
                    self._tunnel_state.connected = True
                    self._tunnel_state.public_port = public_port
                    
                    # Notify GUI
                    self._event_bridge.put_event("connected", {"public_port": public_port})
                    
                    # Start monitoring connections
                    asyncio.create_task(self._monitor_connections())
                    
                    logger.info("Connected successfully")
                
                except AuthenticationError as e:
                    # Authentication error - show user-friendly message
                    self._event_bridge.put_event("connection_error", {"message": str(e)})
                    self._event_bridge.put_event("disconnected", {})
                except Exception as e:
                    logger.error(f"Connection failed: {e}", exc_info=True)
                    self._event_bridge.put_event("connection_error", {"message": f"Ошибка подключения: {e}"})
                    self._event_bridge.put_event("disconnected", {})
            
            asyncio.run_coroutine_threadsafe(do_connect(), self._loop)
        
        threading.Thread(target=connect_async, daemon=True).start()
    
    def _on_disconnect_requested(self) -> None:
        """Handle disconnect request from GUI."""
        def disconnect_async():
            async def do_disconnect():
                try:
                    await self._disconnect_uc.execute()
                    self._event_bridge.put_event("disconnected", {})
                    logger.info("Disconnected successfully")
                except Exception as e:
                    logger.error(f"Disconnect failed: {e}", exc_info=True)
            
            asyncio.run_coroutine_threadsafe(do_disconnect(), self._loop)
        
        threading.Thread(target=disconnect_async, daemon=True).start()
    
    async def _monitor_connections(self) -> None:
        """Monitor active connections and update GUI."""
        import time
        
        last_time = time.time()
        last_bytes_sent = 0
        last_bytes_received = 0
        
        while self._tunnel_state.connected:
            count = self._tunnel_state.get_connection_count()
            self._event_bridge.put_event("connections_changed", {"count": count})
            
            # Calculate statistics
            current_time = time.time()
            bytes_sent = getattr(self._tunnel_state, '_bytes_sent', 0)
            bytes_received = getattr(self._tunnel_state, '_bytes_received', 0)
            
            # Calculate speed (bytes per second)
            time_diff = current_time - last_time
            if time_diff > 0:
                send_speed = (bytes_sent - last_bytes_sent) / time_diff
                receive_speed = (bytes_received - last_bytes_received) / time_diff
            else:
                send_speed = 0.0
                receive_speed = 0.0
            
            # Update statistics
            self._event_bridge.put_event("statistics_updated", {
                "bytes_sent": bytes_sent,
                "bytes_received": bytes_received,
                "send_speed": send_speed,
                "receive_speed": receive_speed
            })
            
            last_time = current_time
            last_bytes_sent = bytes_sent
            last_bytes_received = bytes_received
            
            await asyncio.sleep(0.5)
    
    def stop(self) -> None:
        """Stop the client."""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)


def main() -> None:
    """Main entry point."""
    setup_logging()
    
    client = TunnelClient()
    
    try:
        client.start_gui()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        client.stop()


if __name__ == '__main__':
    main()

