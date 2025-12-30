"""Logs view."""

import customtkinter as ctk
from typing import TextIO
import sys


class LogsView(ctk.CTkFrame):
    """View for logs."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self._setup_ui()
        self._setup_logging()
    
    def _setup_ui(self) -> None:
        """Setup UI components."""
        ctk.CTkLabel(self, text="Logs", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, pady=(10, 10), sticky="ew"
        )
        
        # Text widget with scrollbar
        self._text_widget = ctk.CTkTextbox(self, width=600, height=300)
        self._text_widget.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
    
    def _setup_logging(self) -> None:
        """Setup logging to text widget."""
        import logging
        
        class TextWidgetHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self._text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self._text_widget.insert("end", msg + "\n")
                self._text_widget.see("end")
        
        # Add handler to root logger
        handler = TextWidgetHandler(self._text_widget)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
    
    def add_log(self, message: str) -> None:
        """Add a log message."""
        self._text_widget.insert("end", message + "\n")
        self._text_widget.see("end")
    
    def clear_logs(self) -> None:
        """Clear all logs."""
        self._text_widget.delete("1.0", "end")

