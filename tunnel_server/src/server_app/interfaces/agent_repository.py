"""Agent repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from ..domain.entities.agent_session import AgentSession


class IAgentRepository(ABC):
    """Interface for agent session storage."""
    
    @abstractmethod
    async def save(self, session: AgentSession) -> None:
        """Save an agent session."""
        pass
    
    @abstractmethod
    async def get_by_id(self, agent_id: str) -> Optional[AgentSession]:
        """Get an agent session by ID."""
        pass
    
    @abstractmethod
    async def get_by_port(self, public_port: int) -> Optional[AgentSession]:
        """Get an agent session by public port."""
        pass
    
    @abstractmethod
    async def remove(self, agent_id: str) -> None:
        """Remove an agent session."""
        pass
    
    @abstractmethod
    async def get_all(self) -> list[AgentSession]:
        """Get all agent sessions."""
        pass

