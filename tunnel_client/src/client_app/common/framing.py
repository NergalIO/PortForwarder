"""Binary framing for tunnel protocol."""

import struct
from typing import Optional

MAX_PAYLOAD = 1024 * 1024  # 1 MiB

# Message types
HELLO = 1
WELCOME = 2
OPEN = 3
DATA = 4
CLOSE = 5


class FrameEncoder:
    """Encodes messages into binary frames."""
    
    @staticmethod
    def encode(message_type: int, conn_id: int, payload: bytes) -> bytes:
        """
        Encode a message into a binary frame.
        
        Format: type (uint8) + conn_id (uint32) + length (uint32 BE) + payload
        """
        if len(payload) > MAX_PAYLOAD:
            raise ValueError(f"Payload too large: {len(payload)} > {MAX_PAYLOAD}")
        
        header = struct.pack('>BII', message_type, conn_id, len(payload))
        return header + payload


class FrameDecoder:
    """Decodes binary frames into messages."""
    
    HEADER_SIZE = 9  # 1 + 4 + 4
    
    def __init__(self):
        self._buffer = b''
    
    def feed(self, data: bytes) -> None:
        """Feed data into the decoder buffer."""
        self._buffer += data
    
    def decode(self) -> Optional[tuple[int, int, bytes]]:
        """
        Try to decode a frame from the buffer.
        
        Returns:
            (message_type, conn_id, payload) or None if not enough data
        """
        if len(self._buffer) < self.HEADER_SIZE:
            return None
        
        message_type, conn_id, payload_length = struct.unpack(
            '>BII', self._buffer[:self.HEADER_SIZE]
        )
        
        if payload_length > MAX_PAYLOAD:
            raise ValueError(f"Payload length too large: {payload_length}")
        
        total_size = self.HEADER_SIZE + payload_length
        if len(self._buffer) < total_size:
            return None
        
        payload = self._buffer[self.HEADER_SIZE:total_size]
        self._buffer = self._buffer[total_size:]
        
        return (message_type, conn_id, payload)
    
    def clear(self) -> None:
        """Clear the decoder buffer."""
        self._buffer = b''

