"""Public listener factory interface."""

from abc import ABC, abstractmethod
from typing import Callable, Awaitable


class IPublicListenerFactory(ABC):
    """Interface for creating public listeners."""
    
    @abstractmethod
    async def create_listener(
        self,
        port: int,
        connection_handler: Callable[[object, object], Awaitable[None]]
    ) -> object:
        """
        Create a listener on the given port.
        
        Returns:
            A listener object that can be closed.
        """
        pass

