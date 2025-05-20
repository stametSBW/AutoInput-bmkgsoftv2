"""
Configuration management for the BMKG Auto Input application.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv

class Config:
    """Configuration management class."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        return str(Path(__file__).parent.parent.parent / "config" / "config.yaml")
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Load environment variables
        load_dotenv()
        
        # Load YAML config if exists
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
        
        # Override with environment variables
        self._override_from_env()
    
    def _override_from_env(self) -> None:
        """Override configuration with environment variables."""
        env_mappings = {
            'BMKG_USER_DATA_DIR': ('paths', 'user_data_dir'),
            'BMKG_LOG_LEVEL': ('logging', 'level'),
            'BMKG_BROWSER_TYPE': ('browser', 'type'),
            'BMKG_BROWSER_HEADLESS': ('browser', 'headless'),
            'BMKG_TIMEOUT': ('browser', 'timeout'),
        }
        
        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                self._set_nested_value(self.config_data, config_path, os.environ[env_var])
    
    def _set_nested_value(self, d: Dict[str, Any], path: tuple, value: Any) -> None:
        """Set a value in a nested dictionary using a tuple path."""
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            The configuration value
        """
        try:
            value = self.config_data
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key (dot notation supported)
            value: The value to set
        """
        keys = key.split('.')
        self._set_nested_value(self.config_data, tuple(keys), value)
    
    def save(self) -> None:
        """Save the current configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config_data, f, default_flow_style=False)

# Default configuration
DEFAULT_CONFIG = {
    'paths': {
        'user_data_dir': str(Path.home() / "Documents" / "autoinput"),
        'log_dir': "logs",
    },
    'logging': {
        'level': "INFO",
        'max_size': 10485760,  # 10MB
        'backup_count': 5,
    },
    'browser': {
        'type': "chromium",
        'headless': False,
        'timeout': 30000,  # 30 seconds
    },
    'ui': {
        'window_size': "600x400",
        'theme': "default",
    },
    'automation': {
        'retry_count': 3,
        'retry_delay': 1000,  # 1 second
    }
}

# Create default config file if it doesn't exist
def init_config() -> Config:
    """Initialize configuration with default values."""
    config = Config()
    if not os.path.exists(config.config_path):
        config.config_data = DEFAULT_CONFIG
        config.save()
    return config

# Initialize configuration
config = init_config() 