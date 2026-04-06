import logging
import os
from pathlib import Path

def get_logger(name: str) -> logging.Logger:
    """
    Centralized logging module.
    Log to both console (INFO level) and logs/esim_tool_manager.log (DEBUG level).
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "esim_tool_manager.log"
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers if logger is already configured
    if not logger.handlers:
        # File handler (DEBUG level)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] — %(message)s')
        file_handler.setFormatter(file_format)
        
        # Console handler (INFO level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('[%(levelname)s] [%(name)s] — %(message)s')
        console_handler.setFormatter(console_format)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger
