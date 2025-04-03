from aiogram import BaseMiddleware, Router
from aiogram.types import TelegramObject, Message, CallbackQuery, Update
from typing import Dict, Any, Callable, Awaitable
import time
import logging
import json
import inspect

logger = logging.getLogger("middleware")

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
        
        # Извлекаем сообщение, учитывая разные типы обновлений
        message = None
        if isinstance(event, Update):
            # Проверяем все возможные места, где может быть сообщение
            if event.message:
                message = event.message
            elif event.callback_query:
                message = event.callback_query
            elif event.edited_message:
                message = event.edited_message
            elif event.channel_post:
                message = event.channel_post
            elif event.edited_channel_post:
                message = event.edited_channel_post
            elif event.inline_query:
                from_user = event.inline_query.from_user
                user_id = from_user.id if from_user else None
                username = from_user.username if from_user else None
            elif event.chosen_inline_result:
                from_user = event.chosen_inline_result.from_user
                user_id = from_user.id if from_user else None
                username = from_user.username if from_user else None
            elif hasattr(event, 'from_') and event.from_:
                user_id = event.from_.id
                username = event.from_.username or f"user_{user_id}"
        else:
            message = event if isinstance(event, (Message, CallbackQuery)) else None
            
        # Теперь извлекаем информацию о пользователе
        if message:
            # Для сообщений
            if isinstance(message, Message) and hasattr(message, 'from_user') and message.from_user:
                user_id = message.from_user.id
                username = message.from_user.username or f"user_{user_id}"
                if hasattr(message, 'chat') and message.chat:
                    chat_id = message.chat.id
                    
            # Для callback запросов
            elif isinstance(message, CallbackQuery):
                if hasattr(message, 'from_user') and message.from_user:
                    user_id = message.from_user.id
                    username = message.from_user.username or f"user_{user_id}"
                if hasattr(message, 'message') and message.message and hasattr(message.message, 'chat'):
                    chat_id = message.message.chat.id
            
        # Обрабатываем сообщения и callback запросы
        if isinstance(message, Message) and hasattr(message, 'text') and message.text:
            if message.text.startswith('/'):
                # Log command
                command = message.text.split()[0]
                # Используем extra параметр - самый простой способ
                logger.info(
                    f"Command received: {command}", 
                    extra={"command_name": command, "username": username}
                )
            elif any(keyword in message.text for keyword in ["Мой статус", "Сегодня", "Фокус", "Квесты", "Новый квест", "Завершить", "Инсайт", "Рефлексия", "Настройки", "Помощь", "Удалить квест"]):
                # Log keyboard button press
                command = message.text.strip()
                # Используем extra параметр
                logger.info(
                    f"Button pressed: {command}", 
                    extra={"command_name": command, "username": username}
                )
        elif isinstance(message, CallbackQuery) and hasattr(message, 'data') and message.data:
            # Log callback query
            command = message.data
            # Используем extra параметр
            logger.info(
                f"Callback query: {command}", 
                extra={"command_name": command, "username": username}
            )
            
        try:
            # Handle the event
            result = await handler(event, data)
            # Log success
            processing_time = time.time() - start_time
            
            # Здесь не выводим стандартные логи обработки, т.к. мы уже логируем команды и кнопки
            
            return result
        except Exception as e:
            # Log exception
            processing_time = time.time() - start_time
            logger.error(f"Error processing event in {processing_time:.4f}s: {e}", exc_info=True)
            # Re-raise the exception
            raise 