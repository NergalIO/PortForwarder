"""Port allocator interface."""

from abc import ABC, abstractmethod


class IPortAllocator(ABC):
    """Interface for port allocation."""
    
    @abstractmethod
    async def allocate(self) -> int:
        """Allocate a port. Raises PortAllocationError if none available."""
        pass
    
    @abstractmethod
    async def release(self, port: int) -> None:
        """Release a port back to the pool."""
        pass
    
    @abstractmethod
    def get_available_count(self) -> int:
        """Get the number of available ports."""
        pass

