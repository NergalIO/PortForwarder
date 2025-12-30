"""Event bus interface."""

from abc import ABC, abstractmethod
from typing import Callable, Awaitable, Any


class IEventBus(ABC):
    """Interface for event bus."""
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[Any], Awaitable[None]]) -> None:
        """Subscribe to an event type."""
        pass
    
    @abstractmethod
    async def publish(self, event_type: str, event_data: Any) -> None:
        """Publish an event."""
        pass

