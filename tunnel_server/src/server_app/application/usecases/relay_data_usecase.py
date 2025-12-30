"""Relay data use case."""

import logging
from typing import Optional

from ...interfaces.agent_repository import IAgentRepository
from ...common.protocol import ProtocolCodec
from ...common.framing import DATA

logger = logging.getLogger(__name__)


class RelayDataUseCase:
    """Use case for relaying data between external clients and agents."""
    
    def __init__(self, agent_repository: IAgentRepository):
        self._agent_repository = agent_repository
    
    async def relay_to_agent(
        self,
        agent_id: str,
        conn_id: int,
        data: bytes,
        codec: ProtocolCodec
    ) -> bool:
        """
        Relay data from external client to agent.
        
        Returns:
            True if successful, False otherwise
        """
        session = await self._agent_repository.get_by_id(agent_id)
        if not session or not session.control_writer:
            return False
        
        external_conn = session.get_external_connection(conn_id)
        if not external_conn:
            logger.warning(f"Connection {conn_id} not found for agent {agent_id}")
            return False
        
        try:
            data_msg = codec.encode_data(conn_id, data)
            session.control_writer.write(data_msg)
            await session.control_writer.drain()
            return True
        except Exception as e:
            logger.error(f"Failed to relay data to agent: {e}")
            return False
    
    async def relay_to_external(
        self,
        agent_id: str,
        conn_id: int,
        data: bytes
    ) -> bool:
        """
        Relay data from agent to external client.
        
        Returns:
            True if successful, False otherwise
        """
        session = await self._agent_repository.get_by_id(agent_id)
        if not session:
            return False
        
        external_conn = session.get_external_connection(conn_id)
        if not external_conn or not external_conn.writer:
            logger.warning(f"Connection {conn_id} not found or closed for agent {agent_id}")
            return False
        
        try:
            external_conn.writer.write(data)
            await external_conn.writer.drain()
            return True
        except Exception as e:
            logger.error(f"Failed to relay data to external client: {e}")
            return False

