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

class SimpleJsonFormatter(logging.Formatter):
    """
    Simple JSON formatter for standard logging
    """
    def format(self, record):
        # Create a simple log record
        log_record = {
            "level": record.levelname.lower(),
            "function": f"{record.module}:{record.funcName}:{record.lineno}",
            "message": record.getMessage()
        }
        
        # Add extra fields if available in record.__dict__
        if hasattr(record, 'command_name'):
            log_record['command_name'] = record.command_name
        if hasattr(record, 'username'):
            log_record['username'] = record.username
            
        # Get extras from LoggerAdapter
        if hasattr(record, 'args') and isinstance(record.args, dict):
            if 'command_name' in record.args:
                log_record['command_name'] = record.args['command_name']
            if 'username' in record.args:
                log_record['username'] = record.args['username']
            
        return json.dumps(log_record)

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
            
        # Extract extra fields if available
        extras = {}
        if hasattr(record, 'command_name'):
            extras['command_name'] = record.command_name
        if hasattr(record, 'username'):
            extras['username'] = record.username
            
        # Find caller from where the logged message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
            
        # Pass the message to loguru
        logger_instance = logger.bind(**extras) if extras else logger
        logger_instance.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def json_serializer(record):
    """Serialize log record to JSON format."""
    # Base log fields with minimal information
    output = {
        "level": record["level"].name.lower(),
        "function": f"{record['name']}:{record['function']}:{record['line']}",
        "message": record["message"]
    }
    
    # Add command_name and username if available
    if "command_name" in record["extra"]:
        output["command_name"] = record["extra"]["command_name"]
    
    if "username" in record["extra"]:
        output["username"] = record["extra"]["username"]
    
    return json.dumps(output)

def setup_logging():
    """
    Configure logging for the application.
    This sets up both console and file logging with appropriate formatting.
    """
    # Remove default loguru handler
    logger.remove()
    
    # Configure standard logging first
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    
    # Set up console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(SimpleJsonFormatter())
    root_logger.addHandler(console_handler)
    
    # Set up file handler with JSON formatter
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(SimpleJsonFormatter())
    root_logger.addHandler(file_handler)
    
    # Disable aiogram and other library logging to avoid duplicate entries
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Add loguru handlers for our own logging
    logger.add(
        sys.stdout,
        serialize=json_serializer,
        level="INFO",
        enqueue=True,  # Safe for concurrent writes
        backtrace=False,  # Simpler error logs
        diagnose=False,  # Cleaner output
    )
    
    # Add file handler with JSON formatting
    logger.add(
        log_file,
        serialize=json_serializer,
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    
    # Disable uvicorn access logging if needed
    logging.getLogger("uvicorn.access").disabled = True
    
    # Log setup completion
    logging.info("Logging system configured with simple JSON format")
    
    return logger 