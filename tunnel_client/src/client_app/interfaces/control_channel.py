"""Control channel interface."""

from abc import ABC, abstractmethod
from typing import Callable, Awaitable, Any


class IControlChannel(ABC):
    """Interface for control channel communication."""
    
    @abstractmethod
    async def connect(self, host: str, port: int) -> None:
        """Connect to the server."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the server."""
        pass
    
    @abstractmethod
    async def send_hello(self, token: str, local_host: str, local_port: int) -> None:
        """Send HELLO message."""
        pass
    
    @abstractmethod
    async def wait_for_welcome(self) -> int:
        """Wait for WELCOME message and return public port."""
        pass
    
    @abstractmethod
    def set_message_handler(
        self, handler: Callable[[int, int, bytes], Awaitable[None]]
    ) -> None:
        """Set handler for incoming messages (type, conn_id, payload)."""
        pass
    
    @abstractmethod
    async def send_data(self, conn_id: int, data: bytes) -> None:
        """Send DATA message."""
        pass
    
    @abstractmethod
    async def send_close(self, conn_id: int) -> None:
        """Send CLOSE message."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected."""
        pass

