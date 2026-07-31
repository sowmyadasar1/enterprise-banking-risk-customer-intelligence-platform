import logging
import logging.handlers
import os
from pathlib import Path
from config.settings import settings

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Define standard formatter
STANDARD_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Function to setup as many loggers as you want.
    Uses RotatingFileHandler to handle log rotation (max 10MB per file, keep 5 backups).
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times if logger is requested again
    if not logger.handlers:
        file_path = LOG_DIR / log_file
        
        # File Handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(STANDARD_FORMAT)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(STANDARD_FORMAT)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Pre-configured loggers for different modules
etl_logger = setup_logger("etl", "etl.log", level=logging.DEBUG if settings.DEBUG else logging.INFO)
api_logger = setup_logger("api", "api.log", level=logging.DEBUG if settings.DEBUG else logging.INFO)
ml_logger = setup_logger("ml", "ml.log", level=logging.DEBUG if settings.DEBUG else logging.INFO)
warehouse_logger = setup_logger("warehouse", "warehouse.log", level=logging.DEBUG if settings.DEBUG else logging.INFO)
