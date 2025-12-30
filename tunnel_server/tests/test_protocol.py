"""Tests for protocol module."""

import pytest
from src.server_app.common.protocol import ProtocolCodec
from src.server_app.common.framing import HELLO, WELCOME, DATA, CLOSE


def test_hello_encode_decode():
    """Test HELLO message encoding and decoding."""
    codec = ProtocolCodec()
    
    frame = codec.encode_hello("mytoken", "localhost", 8080)
    codec.feed(frame)
    result = codec.decode_frame()
    
    assert result is not None
    msg_type, conn_id, payload = result
    assert msg_type == HELLO
    
    token, host, port = codec.decode_hello(payload)
    assert token == "mytoken"
    assert host == "localhost"
    assert port == 8080


def test_welcome_encode_decode():
    """Test WELCOME message encoding and decoding."""
    codec = ProtocolCodec()
    
    frame = codec.encode_welcome(10001)
    codec.feed(frame)
    result = codec.decode_frame()
    
    assert result is not None
    msg_type, conn_id, payload = result
    assert msg_type == WELCOME
    
    port = codec.decode_welcome(payload)
    assert port == 10001


def test_data_encode_decode():
    """Test DATA message encoding and decoding."""
    codec = ProtocolCodec()
    
    data = b"test data"
    frame = codec.encode_data(123, data)
    codec.feed(frame)
    result = codec.decode_frame()
    
    assert result is not None
    msg_type, conn_id, payload = result
    assert msg_type == DATA
    assert conn_id == 123
    assert codec.decode_data(payload) == data


def test_close_encode():
    """Test CLOSE message encoding."""
    codec = ProtocolCodec()
    
    frame = codec.encode_close(456)
    codec.feed(frame)
    result = codec.decode_frame()
    
    assert result is not None
    msg_type, conn_id, payload = result
    assert msg_type == CLOSE
    assert conn_id == 456

