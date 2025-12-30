"""Local transport interface."""

from abc import ABC, abstractmethod
from typing import Callable, Awaitable


class ILocalTransport(ABC):
    """Interface for local transport connections."""
    
    @abstractmethod
    async def connect(self, host: str, port: int) -> tuple[object, object]:
        """
        Connect to local service.
        
        Returns:
            (reader, writer) tuple
        """
        pass

