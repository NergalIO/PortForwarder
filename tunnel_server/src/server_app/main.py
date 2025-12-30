"""Main entry point for tunnel server."""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

# Add src directory to path for direct execution
# This allows running the script directly: python main.py
# Also works when imported as a module
_file_path = Path(__file__).resolve()
_src_path = _file_path.parent.parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Use absolute imports after adding src to path
# Try relative import first (when imported as module), then absolute
try:
    from .presentation.cli import parse_args
except ImportError:
    from server_app.presentation.cli import parse_args
# Try relative imports first, then absolute
try:
    from ..infrastructure.logging.logging_adapter import setup_logging
    from ..infrastructure.network.asyncio_control_server import AsyncioControlServer
    from ..infrastructure.network.asyncio_public_listener import AsyncioPublicListenerFactory
    from ..infrastructure.allocators.range_port_allocator import RangePortAllocator
    from ..infrastructure.persistence.in_memory_registry import InMemoryAgentRegistry
    from ..application.usecases.register_agent_usecase import RegisterAgentUseCase
    from ..application.usecases.open_external_connection_usecase import OpenExternalConnectionUseCase
    from ..application.usecases.relay_data_usecase import RelayDataUseCase
    from ..application.usecases.close_connection_usecase import CloseConnectionUseCase
    from ..common.protocol import ProtocolCodec
    from ..common.framing import HELLO, DATA, CLOSE
    from ..common.errors import AuthenticationError, ProtocolError
except ImportError:
    from server_app.infrastructure.logging.logging_adapter import setup_logging
    from server_app.infrastructure.network.asyncio_control_server import AsyncioControlServer
    from server_app.infrastructure.network.asyncio_public_listener import AsyncioPublicListenerFactory
    from server_app.infrastructure.allocators.range_port_allocator import RangePortAllocator
    from server_app.infrastructure.persistence.in_memory_registry import InMemoryAgentRegistry
    from server_app.application.usecases.register_agent_usecase import RegisterAgentUseCase
    from server_app.application.usecases.open_external_connection_usecase import OpenExternalConnectionUseCase
    from server_app.application.usecases.relay_data_usecase import RelayDataUseCase
    from server_app.application.usecases.close_connection_usecase import CloseConnectionUseCase
    from server_app.common.protocol import ProtocolCodec
    from server_app.common.framing import HELLO, DATA, CLOSE
    from server_app.common.errors import AuthenticationError, ProtocolError

logger = logging.getLogger(__name__)


class TunnelServer:
    """Main tunnel server application."""
    
    def __init__(self, config):
        self._config = config
        self._control_server = AsyncioControlServer()
        self._public_listener_factory = AsyncioPublicListenerFactory()
        self._port_allocator = RangePortAllocator(config.port_min, config.port_max)
        self._agent_repository = InMemoryAgentRegistry()
        
        # Use cases
        self._register_agent_uc = RegisterAgentUseCase(
            self._agent_repository,
            self._port_allocator,
            self._public_listener_factory,
            config.token
        )
        self._open_external_uc = OpenExternalConnectionUseCase(self._agent_repository)
        self._relay_data_uc = RelayDataUseCase(self._agent_repository)
        self._close_connection_uc = CloseConnectionUseCase(
            self._agent_repository,
            self._port_allocator
        )
        
        self._running = False
    
    async def start(self) -> None:
        """Start the server."""
        self._running = True
        
        # Setup control server handler
        self._control_server.set_connection_handler(self._handle_control_connection)
        
        # Start control server
        await self._control_server.start(self._config.bind, self._config.control_port)
        
        logger.info(
            f"Tunnel server started: "
            f"control={self._config.bind}:{self._config.control_port}, "
            f"port range=[{self._config.port_min}, {self._config.port_max}]"
        )
    
    async def stop(self) -> None:
        """Stop the server."""
        self._running = False
        await self._control_server.stop()
        
        # Close all agent sessions
        sessions = await self._agent_repository.get_all()
        for session in sessions:
            await self._close_connection_uc.close_agent_session(session.agent_id)
        
        logger.info("Tunnel server stopped")
    
    async def _handle_control_connection(self, reader, writer) -> None:
        """Handle a new control connection from an agent."""
        codec = ProtocolCodec()
        session = None
        
        try:
            # Read HELLO message
            hello_data = await reader.read(4096)
            if not hello_data:
                return
            
            codec.feed(hello_data)
            frame = codec.decode_frame()
            
            if not frame or frame[0] != HELLO:
                logger.error("Expected HELLO message")
                return
            
            # Decode HELLO
            try:
                token, local_host, local_port = codec.decode_hello(frame[2])
            except Exception as e:
                logger.error(f"Failed to decode HELLO: {e}")
                return
            
            # Register agent
            try:
                session = await self._register_agent_uc.execute(
                    token, local_host, local_port, reader, writer, codec
                )
                
                if not session:
                    return
                
                # Create public listener for this session
                listener = await self._public_listener_factory.create_listener(
                    session.public_port,
                    lambda r, w: self._handle_external_connection(session, r, w)
                )
                session._listener = listener
                
                # Process messages from agent
                await self._process_agent_messages(session, codec)
            except AuthenticationError:
                logger.warning("Authentication failed")
                writer.close()
                await writer.wait_closed()
                return
            except Exception as e:
                logger.error(f"Error registering agent: {e}", exc_info=True)
                return
        
        except Exception as e:
            logger.error(f"Error in control connection: {e}", exc_info=True)
        finally:
            if session:
                await self._close_connection_uc.close_agent_session(session.agent_id)
    
    async def _handle_external_connection(self, session, reader, writer) -> None:
        """Handle a new external client connection."""
        codec = ProtocolCodec()
        
        # Open connection with agent
        external_conn = await self._open_external_uc.execute(
            session.public_port, reader, writer, codec
        )
        
        if not external_conn:
            return
        
        try:
            # Relay data: external -> agent
            async def relay_external_to_agent():
                try:
                    while True:
                        data = await reader.read(4096)
                        if not data:
                            break
                        await self._relay_data_uc.relay_to_agent(
                            session.agent_id, external_conn.conn_id, data, codec
                        )
                except Exception as e:
                    logger.debug(f"External->Agent relay ended: {e}")
                finally:
                    await self._close_connection_uc.close_external_connection(
                        session.agent_id, external_conn.conn_id, codec
                    )
            
            # Start relay task
            relay_task = asyncio.create_task(relay_external_to_agent())
            
            # Wait for relay to complete
            await relay_task
            
        except Exception as e:
            logger.error(f"Error in external connection: {e}", exc_info=True)
            await self._close_connection_uc.close_external_connection(
                session.agent_id, external_conn.conn_id, codec
            )
    
    async def _process_agent_messages(self, session, codec: ProtocolCodec) -> None:
        """Process messages from the agent."""
        reader = session.control_reader
        writer = session.control_writer
        
        if not reader or not writer:
            return
        
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                
                codec.feed(data)
                
                while True:
                    frame = codec.decode_frame()
                    if not frame:
                        break
                    
                    msg_type, conn_id, payload = frame
                    
                    if msg_type == DATA:
                        # Relay data from agent to external client
                        await self._relay_data_uc.relay_to_external(
                            session.agent_id, conn_id, payload
                        )
                    elif msg_type == CLOSE:
                        # Close connection requested by agent
                        await self._close_connection_uc.close_agent_connection(
                            session.agent_id, conn_id
                        )
                    else:
                        logger.warning(f"Unexpected message type: {msg_type}")
        
        except Exception as e:
            logger.error(f"Error processing agent messages: {e}", exc_info=True)
        finally:
            # Connection closed
            pass


async def main_async() -> None:
    """Async main function."""
    config = parse_args()
    setup_logging()
    
    server = TunnelServer(config)
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(server.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await server.start()
        
        # Keep running
        while server._running:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        await server.stop()


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

