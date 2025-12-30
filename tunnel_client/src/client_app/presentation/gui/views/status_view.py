"""Status view."""

import customtkinter as ctk
from typing import Optional


class StatusView(ctk.CTkFrame):
    """View for connection status."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self._setup_ui()
        self.update_status(False, None, 0)
    
    def _setup_ui(self) -> None:
        """Setup UI components."""
        # Status section header - centered
        ctk.CTkLabel(self, text="Status", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, pady=(10, 20), sticky="ew"
        )
        
        # Connection status
        ctk.CTkLabel(self, text="Connection:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self._status_label = ctk.CTkLabel(self, text="Disconnected", text_color="red")
        self._status_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Public port
        ctk.CTkLabel(self, text="Public Port:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self._public_port_label = ctk.CTkLabel(self, text="N/A")
        self._public_port_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Active connections
        ctk.CTkLabel(self, text="Active Connections:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self._connections_label = ctk.CTkLabel(self, text="0")
        self._connections_label.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # Statistics section header - centered
        ctk.CTkLabel(self, text="Statistics", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=4, column=0, columnspan=2, pady=(20, 10), sticky="ew"
        )
        
        # Bytes sent
        ctk.CTkLabel(self, text="Bytes Sent:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self._bytes_sent_label = ctk.CTkLabel(self, text="0 B")
        self._bytes_sent_label.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        
        # Bytes received
        ctk.CTkLabel(self, text="Bytes Received:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self._bytes_received_label = ctk.CTkLabel(self, text="0 B")
        self._bytes_received_label.grid(row=6, column=1, padx=10, pady=5, sticky="w")
        
        # Send speed
        ctk.CTkLabel(self, text="Send Speed:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self._send_speed_label = ctk.CTkLabel(self, text="0 B/s")
        self._send_speed_label.grid(row=7, column=1, padx=10, pady=5, sticky="w")
        
        # Receive speed
        ctk.CTkLabel(self, text="Receive Speed:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
        self._receive_speed_label = ctk.CTkLabel(self, text="0 B/s")
        self._receive_speed_label.grid(row=8, column=1, padx=10, pady=5, sticky="w")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
    def update_status(
        self, connected: bool, public_port: Optional[int] = None, active_connections: int = 0
    ) -> None:
        """Update status display."""
        if connected:
            self._status_label.configure(text="Connected", text_color="green")
        else:
            self._status_label.configure(text="Disconnected", text_color="red")
        
        if public_port is not None:
            self._public_port_label.configure(text=str(public_port))
        else:
            self._public_port_label.configure(text="N/A")
        
        self._connections_label.configure(text=str(active_connections))
    
    def update_statistics(self, bytes_sent: int, bytes_received: int, send_speed: float, receive_speed: float) -> None:
        """Update statistics display."""
        def format_bytes(bytes_count: int) -> str:
            """Format bytes to human readable format."""
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_count < 1024.0:
                    return f"{bytes_count:.2f} {unit}"
                bytes_count /= 1024.0
            return f"{bytes_count:.2f} TB"
        
        def format_speed(speed: float) -> str:
            """Format speed to human readable format."""
            for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
                if speed < 1024.0:
                    return f"{speed:.2f} {unit}"
                speed /= 1024.0
            return f"{speed:.2f} TB/s"
        
        self._bytes_sent_label.configure(text=format_bytes(bytes_sent))
        self._bytes_received_label.configure(text=format_bytes(bytes_received))
        self._send_speed_label.configure(text=format_speed(send_speed))
        self._receive_speed_label.configure(text=format_speed(receive_speed))

