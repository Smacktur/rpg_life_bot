import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Make sure logs directory exists
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Get current date for log file name
current_date = datetime.now().strftime("%Y-%m-%d")
log_file = logs_dir / f"{current_date}.log"

class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages toward Loguru.
    
    This handler intercepts all standard logging messages and redirects them to loguru,
    which provides better formatting and handling.
    """
    
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
            
        # Find caller from where the logged message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
            
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    """
    Configure logging for the application.
    This sets up both console and file logging with appropriate formatting.
    """
    # Remove default loguru handler
    logger.remove()
    
    # Add console handler with color formatting
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level="INFO",
        colorize=True,
    )
    
    # Add file handler with detailed formatting
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip",
    )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # Disable uvicorn access logging if needed
    logging.getLogger("uvicorn.access").disabled = True
    
    # Replace standard logger with loguru
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = [InterceptHandler()]
        
    logging.getLogger("root").handlers = [InterceptHandler()]
    
    logger.info("Logging system configured")
    
    return logger 