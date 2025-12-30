"""Bridge between asyncio and GUI thread."""

import asyncio
import queue
import threading
from typing import Callable, Any, Optional


class ThreadingBridge:
    """Bridges asyncio events to GUI thread via queue."""
    
    def __init__(self, gui_callback: Callable[[str, Any], None]):
        """
        Initialize the bridge.
        
        Args:
            gui_callback: Function to call in GUI thread with (event_type, data)
        """
        self._queue: queue.Queue = queue.Queue()
        self._gui_callback = gui_callback
        self._running = False
    
    def put_event(self, event_type: str, data: Any = None) -> None:
        """Put an event in the queue (call from asyncio thread)."""
        self._queue.put((event_type, data))
    
    def poll_events(self) -> None:
        """Poll events from queue and call GUI callback (call from GUI thread)."""
        try:
            while True:
                event_type, data = self._queue.get_nowait()
                self._gui_callback(event_type, data)
        except queue.Empty:
            pass
    
    def start_polling(self, root, interval_ms: int = 100) -> None:
        """Start polling events using root.after."""
        if not self._running:
            self._running = True
            self._poll_loop(root, interval_ms)
    
    def _poll_loop(self, root, interval_ms: int) -> None:
        """Internal polling loop."""
        if self._running:
            self.poll_events()
            root.after(interval_ms, lambda: self._poll_loop(root, interval_ms))
    
    def stop_polling(self) -> None:
        """Stop polling events."""
        self._running = False

