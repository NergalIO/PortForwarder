"""Close connection use case."""

import logging
from typing import Optional

from ...interfaces.agent_repository import IAgentRepository
from ...interfaces.port_allocator import IPortAllocator
from ...common.protocol import ProtocolCodec
from ...common.framing import CLOSE

logger = logging.getLogger(__name__)


class CloseConnectionUseCase:
    """Use case for closing connections."""
    
    def __init__(
        self,
        agent_repository: IAgentRepository,
        port_allocator: IPortAllocator
    ):
        self._agent_repository = agent_repository
        self._port_allocator = port_allocator
    
    async def close_external_connection(
        self,
        agent_id: str,
        conn_id: int,
        codec: ProtocolCodec
    ) -> None:
        """Close an external connection and notify the agent."""
        session = await self._agent_repository.get_by_id(agent_id)
        if not session:
            return
        
        external_conn = session.get_external_connection(conn_id)
        if not external_conn:
            return
        
        # Close external connection
        await external_conn.close()
        session.remove_external_connection(conn_id)
        
        # Notify agent
        if session.control_writer:
            try:
                close_msg = codec.encode_close(conn_id)
                session.control_writer.write(close_msg)
                await session.control_writer.drain()
                logger.info(f"Closed external connection {conn_id} for agent {agent_id}")
            except Exception as e:
                logger.error(f"Failed to send CLOSE message: {e}")
    
    async def close_agent_connection(
        self,
        agent_id: str,
        conn_id: int
    ) -> None:
        """Close a connection requested by the agent."""
        session = await self._agent_repository.get_by_id(agent_id)
        if not session:
            return
        
        external_conn = session.get_external_connection(conn_id)
        if not external_conn:
            return
        
        # Close external connection
        await external_conn.close()
        session.remove_external_connection(conn_id)
        logger.info(f"Closed connection {conn_id} for agent {agent_id}")
    
    async def close_agent_session(self, agent_id: str) -> None:
        """Close an entire agent session and all its connections."""
        session = await self._agent_repository.get_by_id(agent_id)
        if not session:
            return
        
        # Close all external connections
        for conn in session.get_all_connections():
            await conn.close()
        
        # Close control connection
        if session.control_writer:
            try:
                session.control_writer.close()
                await session.control_writer.wait_closed()
            except Exception:
                pass
        
        # Close public listener
        if hasattr(session, '_listener'):
            await session._listener.close()
        
        # Release port
        await self._port_allocator.release(session.public_port)
        
        # Remove from repository
        await self._agent_repository.remove(agent_id)
        
        logger.info(f"Closed agent session {agent_id}")

