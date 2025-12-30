"""Control server interface."""

from abc import ABC, abstractmethod
from typing import Callable, Awaitable


class IControlServer(ABC):
    """Interface for control server."""
    
    @abstractmethod
    async def start(self, host: str, port: int) -> None:
        """Start the control server."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the control server."""
        pass
    
    @abstractmethod
    def set_connection_handler(
        self, handler: Callable[[object, object], Awaitable[None]]
    ) -> None:
        """Set the handler for new connections."""
        pass

