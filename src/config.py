from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import json
import os
from pathlib import Path

@dataclass
class RetryConfig:
    max_retries: int = 5
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0

@dataclass
class NetworkConfig:
    page_load_timeout: int = 30000
    navigation_timeout: int = 30000
    retry_interval: int = 60
    max_network_retries: int = 3

@dataclass
class AutoSenderConfig:
    headless: bool = False
    retry: RetryConfig = field(default_factory=RetryConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    log_level: str = "INFO"
    base_url: str = "https://bmkgsatu.bmkg.go.id/meteorologi/sinoptik"

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AutoSenderConfig':
        """Create config from dictionary."""
        retry_config = RetryConfig(**config_dict.get('retry', {}))
        network_config = NetworkConfig(**config_dict.get('network', {}))
        return cls(
            headless=config_dict.get('headless', False),
            retry=retry_config,
            network=network_config,
            log_level=config_dict.get('log_level', 'INFO'),
            base_url=config_dict.get('base_url', cls.base_url)
        )

    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> 'AutoSenderConfig':
        """Load configuration from file."""
        if config_path is None:
            config_path = os.getenv('AUTO_SENDER_CONFIG', 'config.json')
        
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            return cls.from_dict(config_dict)
        except FileNotFoundError:
            return cls()  # Return default config if file not found
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config file: {str(e)}", e) 