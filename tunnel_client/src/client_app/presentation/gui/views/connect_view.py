"""Connect view."""

import customtkinter as ctk
from typing import Callable, Optional


class ConnectView(ctk.CTkFrame):
    """View for connection settings."""
    
    def __init__(self, parent, on_connect: Optional[Callable] = None, on_disconnect: Optional[Callable] = None):
        super().__init__(parent)
        
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup UI components."""
        # Server settings
        ctk.CTkLabel(self, text="Server Settings", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 20), sticky="ew"
        )
        
        ctk.CTkLabel(self, text="Server Host:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self._server_host_entry = ctk.CTkEntry(self, width=200)
        self._server_host_entry.insert(0, "localhost")
        self._server_host_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(self, text="Server Port:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self._server_port_entry = ctk.CTkEntry(self, width=200)
        self._server_port_entry.insert(0, "7000")
        self._server_port_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(self, text="Token:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self._token_entry = ctk.CTkEntry(self, width=200, show="*")
        self._token_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        # Local settings
        ctk.CTkLabel(self, text="Local Settings", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=4, column=0, columnspan=2, pady=(20, 10), sticky="ew"
        )
        
        ctk.CTkLabel(self, text="Local Port:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self._local_port_entry = ctk.CTkEntry(self, width=200)
        self._local_port_entry.insert(0, "8080")
        self._local_port_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        
        # Buttons
        self._connect_btn = ctk.CTkButton(
            self, text="Connect", command=self._on_connect_clicked, width=150
        )
        self._connect_btn.grid(row=6, column=0, columnspan=2, pady=20)
        
        self._disconnect_btn = ctk.CTkButton(
            self, text="Disconnect", command=self._on_disconnect_clicked, width=150, state="disabled"
        )
        self._disconnect_btn.grid(row=7, column=0, columnspan=2, pady=5)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        if self._on_connect:
            self._on_connect()
    
    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click."""
        if self._on_disconnect:
            self._on_disconnect()
    
    def get_config(self) -> Optional[dict]:
        """Get connection configuration from UI."""
        try:
            return {
                'server_host': self._server_host_entry.get().strip(),
                'server_port': int(self._server_port_entry.get().strip()),
                'token': self._token_entry.get().strip(),
                'local_host': 'localhost',  # Always localhost
                'local_port': int(self._local_port_entry.get().strip())
            }
        except ValueError:
            return None
    
    def set_config(self, config: dict) -> None:
        """Set connection configuration in UI."""
        if 'server_host' in config:
            self._server_host_entry.delete(0, 'end')
            self._server_host_entry.insert(0, config['server_host'])
        if 'server_port' in config:
            self._server_port_entry.delete(0, 'end')
            self._server_port_entry.insert(0, str(config['server_port']))
        if 'token' in config:
            self._token_entry.delete(0, 'end')
            self._token_entry.insert(0, config['token'])
        if 'local_port' in config:
            self._local_port_entry.delete(0, 'end')
            self._local_port_entry.insert(0, str(config['local_port']))
    
    def set_connected(self, connected: bool) -> None:
        """Update UI state based on connection status."""
        if connected:
            self._connect_btn.configure(state="disabled")
            self._disconnect_btn.configure(state="normal")
            # Disable input fields
            self._server_host_entry.configure(state="disabled")
            self._server_port_entry.configure(state="disabled")
            self._token_entry.configure(state="disabled")
            self._local_port_entry.configure(state="disabled")
        else:
            self._connect_btn.configure(state="normal")
            self._disconnect_btn.configure(state="disabled")
            # Enable input fields
            self._server_host_entry.configure(state="normal")
            self._server_port_entry.configure(state="normal")
            self._token_entry.configure(state="normal")
            self._local_port_entry.configure(state="normal")

