"""Configuration manager for saving/loading settings."""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages saving and loading application configuration."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize config manager.
        
        Args:
            config_file: Path to config file. If None, uses default location.
        """
        if config_file is None:
            # Use user's app data directory
            app_data = Path.home() / ".tunnel_client"
            app_data.mkdir(exist_ok=True)
            config_file = app_data / "config.json"
        
        self._config_file = config_file
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            # Don't save token for security
            safe_config = {
                'server_host': config.get('server_host', ''),
                'server_port': config.get('server_port', 7000),
                'local_port': config.get('local_port', 8080),
            }
            
            with open(self._config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)
            
            logger.debug(f"Configuration saved to {self._config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from file."""
        try:
            if not self._config_file.exists():
                return None
            
            with open(self._config_file, 'r') as f:
                config = json.load(f)
            
            logger.debug(f"Configuration loaded from {self._config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return None

