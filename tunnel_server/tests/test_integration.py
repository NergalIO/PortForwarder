"""Integration tests for tunnel server."""

import asyncio
import pytest
import socket
from src.server_app.main import TunnelServer
from src.server_app.presentation.cli import ServerConfig


@pytest.mark.asyncio
async def test_server_start_stop():
    """Test server start and stop."""
    config = ServerConfig(
        bind="127.0.0.1",
        control_port=7001,
        port_min=10001,
        port_max=10010,
        token="testtoken"
    )
    
    server = TunnelServer(config)
    
    try:
        await server.start()
        
        # Check that server is listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("127.0.0.1", 7001))
        sock.close()
        assert result == 0  # Connection successful
        
    finally:
        await server.stop()


@pytest.mark.asyncio
async def test_echo_server_integration():
    """Test integration with echo server."""
    # This is a basic integration test
    # In a real scenario, you would:
    # 1. Start an echo server on localhost:8080
    # 2. Start the tunnel server
    # 3. Connect a client
    # 4. Verify data flows through
    
    # For now, just test that server can start
    config = ServerConfig(
        bind="127.0.0.1",
        control_port=7002,
        port_min=10011,
        port_max=10020,
        token="testtoken"
    )
    
    server = TunnelServer(config)
    
    try:
        await server.start()
        # Server started successfully
        assert True
    finally:
        await server.stop()

