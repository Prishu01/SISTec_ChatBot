

import logging
import sys
from pathlib import Path
from typing import Optional
import platform

from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE


def setup_logger(name: str) -> logging.Logger:
    """
    Configure logger with file and console handlers.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Remove existing handlers to prevent duplicates
    logger.handlers = []
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (IOError, OSError) as e:
        logger.warning(f"Could not create log file: {e}")
    
    return logger


def validate_api_key(api_key: Optional[str]) -> bool:
    """
    Validate Groq API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    return isinstance(api_key, str) and len(api_key) > 20


def validate_file_exists(filepath: str) -> bool:
    """
    Check if file exists and is readable.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if file exists and is readable, False otherwise
    """
    path = Path(filepath)
    return path.exists() and path.is_file() and path.stat().st_size > 0


def validate_duration(duration: int, min_val: int = 1, max_val: int = 120) -> bool:
    """
    Validate recording duration.
    
    Args:
        duration: Duration in seconds
        min_val: Minimum allowed duration
        max_val: Maximum allowed duration
        
    Returns:
        True if duration is valid, False otherwise
    """
    return isinstance(duration, int) and min_val <= duration <= max_val


def get_platform_info() -> str:
    """
    Get current platform information.
    
    Returns:
        Platform name (Windows, Darwin, Linux)
    """
    return platform.system()


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """
    Sanitize and truncate text.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text


def format_duration(seconds: int) -> str:
    """
    Format seconds to readable duration.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}m {secs}s"


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass
