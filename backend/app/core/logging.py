import logging
import logging.handlers
import os
from app.core.config import settings

def setup_logging():
    """Setup logging with rotation"""
    
    # Create logs directory
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))
    root_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))
    root_logger.addHandler(console_handler)
    
    # JSON handler for structured logging in production
    if settings.ENVIRONMENT == "production":
        json_handler = logging.handlers.RotatingFileHandler(
            "logs/app.json",
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT
        )
        json_handler.setFormatter(logging.Formatter(
            '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", '
            '"message": "%(message)s", "module": "%(module)s"}'
        ))
        root_logger.addHandler(json_handler)