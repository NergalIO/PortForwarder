"""Connection view model."""

from dataclasses import dataclass, field
from typing import Optional, Callable


@dataclass
class ConnectionViewModel:
    """View model for connection state."""
    
    server_host: str = ""
    server_port: int = 7000
    token: str = ""
    local_host: str = "localhost"
    local_port: int = 8080
    
    connected: bool = False
    public_port: Optional[int] = None
    active_connections: int = 0
    
    # Statistics
    bytes_sent: int = 0
    bytes_received: int = 0
    send_speed: float = 0.0  # bytes per second
    receive_speed: float = 0.0  # bytes per second
    
    # Callbacks for UI updates
    _on_state_changed: Optional[Callable[[], None]] = field(default=None, repr=False)
    
    def set_state_changed_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for state changes."""
        self._on_state_changed = callback
    
    def notify_state_changed(self) -> None:
        """Notify that state has changed."""
        if self._on_state_changed:
            self._on_state_changed()
    
    def update_connection_status(self, connected: bool, public_port: Optional[int] = None) -> None:
        """Update connection status."""
        self.connected = connected
        if public_port is not None:
            self.public_port = public_port
        self.notify_state_changed()
    
    def update_active_connections(self, count: int) -> None:
        """Update active connections count."""
        self.active_connections = count
        self.notify_state_changed()
    
    def update_statistics(self, bytes_sent: int, bytes_received: int, send_speed: float, receive_speed: float) -> None:
        """Update transfer statistics."""
        self.bytes_sent = bytes_sent
        self.bytes_received = bytes_received
        self.send_speed = send_speed
        self.receive_speed = receive_speed
        self.notify_state_changed()
    
    def reset_statistics(self) -> None:
        """Reset statistics."""
        self.bytes_sent = 0
        self.bytes_received = 0
        self.send_speed = 0.0
        self.receive_speed = 0.0
        self.notify_state_changed()

