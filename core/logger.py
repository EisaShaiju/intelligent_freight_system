import logging
import sys
from core.config import settings

def setup_logger(name: str) -> logging.Logger:
    """
    Creates and configures a standardized logger for the application.
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if the logger is called multiple times
    if not logger.handlers:
        # Set to DEBUG in development to see agent thoughts, INFO in production
        log_level = logging.DEBUG if settings.environment == "development" else logging.INFO
        logger.setLevel(log_level)
        
        # Standardize the log format: [Time] - [Module] - [Level] - [Message]
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Output to the console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

# Create a default global logger for quick imports
logger = setup_logger("ibs_orchestrator")