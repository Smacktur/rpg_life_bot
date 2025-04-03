from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Dict, Any, Callable, Awaitable
import time
from loguru import logger

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
        username = None
        chat_id = None
        command = None
        
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
            username = event.from_user.username or f"user_{user_id}"
            
        if hasattr(event, 'chat') and event.chat:
            chat_id = event.chat.id
        
        # Detect commands and callback data
        if isinstance(event, Message) and event.text:
            if event.text.startswith('/'):
                command = event.text.split()[0]
                # Log command with extra fields
                logger.bind(command=command, username=username).info(f"Command received: {command}")
            elif any(keyword in event.text for keyword in ["Мой статус", "Сегодня", "Фокус", "Квесты", "Новый квест", "Завершить", "Инсайт", "Рефлексия", "Настройки", "Помощь", "Удалить квест"]):
                # Log keyboard button press with extra fields
                command = event.text.strip()
                logger.bind(command=command, username=username).info(f"Button pressed: {command}")
                
        elif isinstance(event, CallbackQuery) and event.data:
            # Log callback query with extra fields
            command = event.data
            logger.bind(command=command, username=username).info(f"Callback query: {command}")
            
        # Log incoming event
        event_name = event.__class__.__name__
        logger.info(f"Processing {event_name} from user={user_id} chat={chat_id}")
        
        try:
            # Handle the event
            result = await handler(event, data)
            # Log success
            processing_time = time.time() - start_time
            logger.info(f"Processed {event_name} in {processing_time:.4f}s")
            return result
        except Exception as e:
            # Log exception
            processing_time = time.time() - start_time
            logger.error(f"Error processing {event_name} in {processing_time:.4f}s: {e}", exc_info=True)
            # Re-raise the exception
            raise 