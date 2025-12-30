"""Open external connection use case."""

import logging
import asyncio
from typing import Optional

from ...interfaces.agent_repository import IAgentRepository
from ...domain.entities.external_conn import ExternalConn
from ...common.protocol import ProtocolCodec
from ...common.framing import OPEN

logger = logging.getLogger(__name__)


class OpenExternalConnectionUseCase:
    """Use case for opening a new external connection."""
    
    def __init__(self, agent_repository: IAgentRepository):
        self._agent_repository = agent_repository
        self._next_conn_id = 1
    
    async def execute(
        self,
        public_port: int,
        external_reader,
        external_writer,
        codec: ProtocolCodec
    ) -> Optional[ExternalConn]:
        """
        Open a new external connection and notify the agent.
        
        Returns:
            ExternalConn if successful, None otherwise
        """
        # Find agent by port
        session = await self._agent_repository.get_by_port(public_port)
        if not session:
            logger.error(f"No agent found for port {public_port}")
            return None
        
        if not session.control_writer:
            logger.error(f"Agent {session.agent_id} has no control writer")
            return None
        
        # Allocate connection ID
        conn_id = self._next_conn_id
        self._next_conn_id = (self._next_conn_id + 1) % (2**32)
        
        # Create external connection
        external_conn = ExternalConn(
            conn_id=conn_id,
            agent_id=session.agent_id,
            reader=external_reader,
            writer=external_writer
        )
        
        # Add to session
        session.add_external_connection(external_conn)
        
        # Send OPEN message to agent
        open_msg = codec.encode_open(conn_id)
        try:
            session.control_writer.write(open_msg)
            await session.control_writer.drain()
            logger.info(f"Opened external connection {conn_id} for agent {session.agent_id}")
        except Exception as e:
            logger.error(f"Failed to send OPEN message: {e}")
            session.remove_external_connection(conn_id)
            return None
        
        return external_conn

