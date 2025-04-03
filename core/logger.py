import logging
import os
import sys
import json
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

def json_serializer(record):
    """Serialize log record to JSON format."""
    # Base log fields
    output = {
        "level": record["level"].name.lower(),
        "function": f"{record['name']}:{record['function']}:{record['line']}",
        "message": record["message"],
        "time": record["time"].strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    # Add extra fields if available
    for k, v in record["extra"].items():
        output[k] = v
    
    return json.dumps(output)

def setup_logging():
    """
    Configure logging for the application.
    This sets up both console and file logging with appropriate formatting.
    """
    # Remove default loguru handler
    logger.remove()
    
    # Add console handler with JSON formatting
    logger.add(
        sys.stdout,
        serialize=json_serializer,
        level="INFO",
    )
    
    # Add file handler with JSON formatting
    logger.add(
        log_file,
        serialize=json_serializer,
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