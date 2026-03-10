"""
Professional Logging Configuration

Centralized logging setup with:
- File rotation
- Different log levels for dev/production
- Structured logging format
- Performance tracking
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


# Create logs directory
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def setup_logger(
    name: str = "talentradar",
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True
) -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to rotating file
        log_to_console: Whether to log to console
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Format: [2026-03-09 14:30:45] [INFO] [module.function] Message
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_to_file:
        log_file = LOGS_DIR / f"{name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,  # Keep 5 backup files
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Separate error log
        error_file = LOGS_DIR / f"{name}_errors.log"
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger


# Create default loggers
app_logger = setup_logger("talentradar")
scraper_logger = setup_logger("scraper", level=logging.DEBUG)
api_logger = setup_logger("api")
db_logger = setup_logger("database")


class PerformanceLogger:
    """Context manager for logging function execution time."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(
                f"Failed: {self.operation} after {duration:.2f}s - {exc_type.__name__}: {exc_val}"
            )
        else:
            self.logger.info(f"Completed: {self.operation} in {duration:.2f}s")
        
        return False  # Don't suppress exceptions


def log_api_request(logger: logging.Logger, method: str, url: str, status: int, duration: float):
    """Log API request details."""
    logger.info(f"{method} {url} - {status} ({duration:.2f}s)")


def log_scraper_progress(logger: logging.Logger, query: str, count: int, source: str):
    """Log scraper progress."""
    logger.info(f"Scraped {count} candidates for '{query}' from {source}")


def log_error_with_context(logger: logging.Logger, error: Exception, context: dict):
    """Log error with additional context."""
    logger.error(
        f"Error: {type(error).__name__}: {str(error)} | Context: {context}",
        exc_info=True
    )
