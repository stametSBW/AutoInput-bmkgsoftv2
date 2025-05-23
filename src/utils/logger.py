"""
Logging configuration for the BMKG Auto Input application.
"""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

class LogConfig:
    """Configuration for application logging."""
    
    def __init__(self, log_dir=None):
        # Set default log directory if none provided
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file paths
        self.app_log = self.log_dir / "app.log"
        self.browser_log = self.log_dir / "browser.log"
        self.error_log = self.log_dir / "error.log"
        
        # Configure loggers
        self._configure_loggers()
    
    def _configure_loggers(self) -> None:
        """Configure all application loggers."""
        # Configure root logger
        self._configure_root_logger()
        
        # Configure specific loggers
        self._configure_app_logger()
        self._configure_browser_logger()
        self._configure_error_logger()
        
        # Log initial configuration
        root_logger = logging.getLogger()
        root_logger.debug("Logging configuration initialized")
        root_logger.debug(f"Log directory: {self.log_dir}")
        root_logger.debug(f"App log: {self.app_log}")
        root_logger.debug(f"Browser log: {self.browser_log}")
        root_logger.debug(f"Error log: {self.error_log}")
    
    def _configure_root_logger(self) -> None:
        """Configure the root logger."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all messages
        
        # Remove any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Root file handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.app_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)  # Capture all messages
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    def _configure_app_logger(self) -> None:
        """Configure the application logger."""
        app_logger = logging.getLogger('app')
        app_logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all messages
        app_logger.propagate = True  # Propagate to root logger
        
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.app_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        app_logger.addHandler(file_handler)
    
    def _configure_browser_logger(self) -> None:
        """Configure the browser automation logger."""
        browser_logger = logging.getLogger('browser')
        browser_logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all messages
        browser_logger.propagate = True  # Propagate to root logger
        
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.browser_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        browser_logger.addHandler(file_handler)
    
    def _configure_error_logger(self) -> None:
        """Configure the error logger."""
        error_logger = logging.getLogger('error')
        error_logger.setLevel(logging.ERROR)
        error_logger.propagate = True  # Propagate to root logger
        
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.error_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.ERROR)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
            'File: %(pathname)s\n'
            'Line: %(lineno)d\n'
            'Function: %(funcName)s\n'
            'Exception: %(exc_info)s\n'
        )
        file_handler.setFormatter(file_formatter)
        error_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Name of the logger
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

def setup_logging(log_dir: Optional[str] = None) -> LogConfig:
    """
    Set up logging configuration for the application.
    
    Args:
        log_dir: Optional directory for log files. Defaults to 'logs'.
        
    Returns:
        LogConfig instance.
    """
    return LogConfig(log_dir)

# Initialize logging when module is imported
log_config = setup_logging() 

def setup_logger(name: str, log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with proper configuration.
    
    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(detailed_formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        file_handler = logging.FileHandler(
            log_dir / f"{log_file}_{timestamp}.log"
        )
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger 