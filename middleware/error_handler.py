from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Dict, Any, Callable, Awaitable
import logging
from aiogram.exceptions import TelegramAPIError

class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Middleware for handling errors and providing user-friendly responses.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except TelegramAPIError as e:
            # Handle Telegram API errors
            logging.error(f"Telegram API error: {e}", exc_info=True)
            
            # Try to inform the user about the error
            try:
                if isinstance(event, Message):
                    await event.answer("Произошла ошибка в работе с Telegram API. Пожалуйста, попробуйте позже.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Ошибка API, попробуйте позже", show_alert=True)
            except Exception as notify_error:
                logging.error(f"Failed to notify user about error: {notify_error}")
                
        except Exception as e:
            # Handle all other errors
            logging.error(f"Unhandled error: {e}", exc_info=True)
            
            # Try to inform the user about the error
            try:
                if isinstance(event, Message):
                    await event.answer("Произошла внутренняя ошибка. Попробуйте позже или другую команду.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Внутренняя ошибка, попробуйте позже", show_alert=True)
            except Exception as notify_error:
                logging.error(f"Failed to notify user about error: {notify_error}") 