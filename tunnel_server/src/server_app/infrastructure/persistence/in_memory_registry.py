"""In-memory agent registry."""

import asyncio
import logging
from typing import Optional, Dict

from ...interfaces.agent_repository import IAgentRepository
from ...domain.entities.agent_session import AgentSession

logger = logging.getLogger(__name__)


class InMemoryAgentRegistry(IAgentRepository):
    """In-memory implementation of agent repository."""
    
    def __init__(self):
        self._sessions: Dict[str, AgentSession] = {}
        self._port_to_agent: Dict[int, str] = {}
        self._lock = asyncio.Lock()
    
    async def save(self, session: AgentSession) -> None:
        """Save an agent session."""
        async with self._lock:
            self._sessions[session.agent_id] = session
            self._port_to_agent[session.public_port] = session.agent_id
            logger.debug(f"Saved agent session: {session.agent_id} on port {session.public_port}")
    
    async def get_by_id(self, agent_id: str) -> Optional[AgentSession]:
        """Get an agent session by ID."""
        async with self._lock:
            return self._sessions.get(agent_id)
    
    async def get_by_port(self, public_port: int) -> Optional[AgentSession]:
        """Get an agent session by public port."""
        async with self._lock:
            agent_id = self._port_to_agent.get(public_port)
            if agent_id:
                return self._sessions.get(agent_id)
            return None
    
    async def remove(self, agent_id: str) -> None:
        """Remove an agent session."""
        async with self._lock:
            session = self._sessions.pop(agent_id, None)
            if session:
                self._port_to_agent.pop(session.public_port, None)
                logger.debug(f"Removed agent session: {agent_id}")
    
    async def get_all(self) -> list[AgentSession]:
        """Get all agent sessions."""
        async with self._lock:
            return list(self._sessions.values())

