"""Range-based port allocator."""

import asyncio
import logging
from typing import Set

from ...interfaces.port_allocator import IPortAllocator
from ...common.errors import PortAllocationError

logger = logging.getLogger(__name__)


class RangePortAllocator(IPortAllocator):
    """Port allocator that manages a range of ports."""
    
    def __init__(self, port_min: int, port_max: int):
        if port_min > port_max:
            raise ValueError("port_min must be <= port_max")
        self._port_min = port_min
        self._port_max = port_max
        self._allocated: Set[int] = set()
        self._lock = asyncio.Lock()
    
    async def allocate(self) -> int:
        """Allocate a port from the range."""
        async with self._lock:
            for port in range(self._port_min, self._port_max + 1):
                if port not in self._allocated:
                    self._allocated.add(port)
                    logger.debug(f"Allocated port {port}")
                    return port
            raise PortAllocationError(
                f"No available ports in range [{self._port_min}, {self._port_max}]"
            )
    
    async def release(self, port: int) -> None:
        """Release a port back to the pool."""
        async with self._lock:
            if port in self._allocated:
                self._allocated.remove(port)
                logger.debug(f"Released port {port}")
            else:
                logger.warning(f"Attempted to release unallocated port {port}")
    
    def get_available_count(self) -> int:
        """Get the number of available ports."""
        return (self._port_max - self._port_min + 1) - len(self._allocated)

