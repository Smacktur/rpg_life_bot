from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Dict, Any, Callable, Awaitable
import logging
import time

class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging all bot events and measuring execution time.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Start timing
        start_time = time.time()
        
        # Extract user and chat info if available
        user_id = None
        chat_id = None
        
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
            
        if hasattr(event, 'chat') and event.chat:
            chat_id = event.chat.id
        
        # Log incoming event
        event_name = event.__class__.__name__
        logging.info(f"Processing {event_name} from user={user_id} chat={chat_id}")
        
        try:
            # Handle the event
            result = await handler(event, data)
            # Log success
            processing_time = time.time() - start_time
            logging.info(f"Processed {event_name} in {processing_time:.4f}s")
            return result
        except Exception as e:
            # Log exception
            processing_time = time.time() - start_time
            logging.error(
                f"Error processing {event_name} in {processing_time:.4f}s: {e}",
                exc_info=True
            )
            # Re-raise the exception
            raise 