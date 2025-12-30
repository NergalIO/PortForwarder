"""Tests for framing module."""

import pytest
from src.client_app.common.framing import FrameEncoder, FrameDecoder, HELLO, DATA, MAX_PAYLOAD


def test_encode_decode():
    """Test encoding and decoding frames."""
    encoder = FrameEncoder()
    decoder = FrameDecoder()
    
    # Test HELLO message
    payload = b"test payload"
    frame = encoder.encode(HELLO, 0, payload)
    assert len(frame) == 9 + len(payload)  # header (9 bytes) + payload
    
    decoder.feed(frame)
    result = decoder.decode()
    assert result is not None
    msg_type, conn_id, payload = result
    assert msg_type == HELLO
    assert conn_id == 0
    assert payload == b"test payload"


def test_encode_decode_with_conn_id():
    """Test encoding and decoding with connection ID."""
    encoder = FrameEncoder()
    decoder = FrameDecoder()
    
    frame = encoder.encode(DATA, 12345, b"data")
    decoder.feed(frame)
    result = decoder.decode()
    assert result is not None
    msg_type, conn_id, payload = result
    assert msg_type == DATA
    assert conn_id == 12345
    assert payload == b"data"

