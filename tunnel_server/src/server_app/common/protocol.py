"""Protocol codec for tunnel messages."""

import struct
from typing import Optional

from .framing import FrameEncoder, FrameDecoder, HELLO, WELCOME, OPEN, DATA, CLOSE


class ProtocolCodec:
    """Encodes and decodes protocol messages."""
    
    def __init__(self):
        self._encoder = FrameEncoder()
        self._decoder = FrameDecoder()
    
    def encode_hello(self, token: str, local_host: str, local_port: int) -> bytes:
        """Encode HELLO message."""
        payload = f"{token}\0{local_host}\0{local_port}".encode('utf-8')
        return self._encoder.encode(HELLO, 0, payload)
    
    def decode_hello(self, payload: bytes) -> tuple[str, str, int]:
        """Decode HELLO message."""
        parts = payload.decode('utf-8').split('\0')
        if len(parts) != 3:
            raise ValueError("Invalid HELLO message format")
        return (parts[0], parts[1], int(parts[2]))
    
    def encode_welcome(self, public_port: int) -> bytes:
        """Encode WELCOME message."""
        payload = struct.pack('>I', public_port)
        return self._encoder.encode(WELCOME, 0, payload)
    
    def decode_welcome(self, payload: bytes) -> int:
        """Decode WELCOME message."""
        return struct.unpack('>I', payload)[0]
    
    def encode_open(self, conn_id: int) -> bytes:
        """Encode OPEN message."""
        return self._encoder.encode(OPEN, conn_id, b'')
    
    def decode_open(self, payload: bytes) -> int:
        """Decode OPEN message (conn_id is in header)."""
        # conn_id is in the frame header, not payload
        pass
    
    def encode_data(self, conn_id: int, data: bytes) -> bytes:
        """Encode DATA message."""
        return self._encoder.encode(DATA, conn_id, data)
    
    def decode_data(self, payload: bytes) -> bytes:
        """Decode DATA message."""
        return payload
    
    def encode_close(self, conn_id: int) -> bytes:
        """Encode CLOSE message."""
        return self._encoder.encode(CLOSE, conn_id, b'')
    
    def decode_close(self, payload: bytes) -> None:
        """Decode CLOSE message."""
        pass
    
    def feed(self, data: bytes) -> None:
        """Feed data to the decoder."""
        self._decoder.feed(data)
    
    def decode_frame(self) -> Optional[tuple[int, int, bytes]]:
        """Decode a frame from the buffer."""
        return self._decoder.decode()
    
    def clear(self) -> None:
        """Clear the decoder buffer."""
        self._decoder.clear()

