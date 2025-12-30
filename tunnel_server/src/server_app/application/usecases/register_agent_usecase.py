"""Register agent use case."""

import logging
import uuid
from typing import Optional

from ...interfaces.agent_repository import IAgentRepository
from ...interfaces.port_allocator import IPortAllocator
from ...interfaces.public_listener_factory import IPublicListenerFactory
from ...domain.entities.agent_session import AgentSession
from ...common.errors import AuthenticationError, PortAllocationError
from ...common.protocol import ProtocolCodec

logger = logging.getLogger(__name__)


class RegisterAgentUseCase:
    """Use case for registering a new agent."""
    
    def __init__(
        self,
        agent_repository: IAgentRepository,
        port_allocator: IPortAllocator,
        public_listener_factory: IPublicListenerFactory,
        expected_token: str
    ):
        self._agent_repository = agent_repository
        self._port_allocator = port_allocator
        self._public_listener_factory = public_listener_factory
        self._expected_token = expected_token
    
    async def execute(
        self,
        token: str,
        local_host: str,
        local_port: int,
        reader,
        writer,
        codec: ProtocolCodec
    ) -> Optional[AgentSession]:
        """
        Register a new agent.
        
        Returns:
            AgentSession if successful, None otherwise
        """
        # Verify token
        if token != self._expected_token:
            logger.warning(f"Authentication failed: invalid token")
            raise AuthenticationError("Invalid token")
        
        # Allocate port
        try:
            public_port = await self._port_allocator.allocate()
        except PortAllocationError as e:
            logger.error(f"Port allocation failed: {e}")
            raise
        
        # Create agent session
        agent_id = str(uuid.uuid4())
        session = AgentSession(
            agent_id=agent_id,
            token=token,
            local_host=local_host,
            local_port=local_port,
            public_port=public_port,
            control_reader=reader,
            control_writer=writer
        )
        
        # Save session first (listener will be created in main.py)
        await self._agent_repository.save(session)
        
        # Send WELCOME message
        welcome_msg = codec.encode_welcome(public_port)
        writer.write(welcome_msg)
        await writer.drain()
        
        logger.info(
            f"Agent registered: {agent_id}, "
            f"local={local_host}:{local_port}, "
            f"public_port={public_port}"
        )
        
        return session

