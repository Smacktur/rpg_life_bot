import asyncio
import os
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, DATA_FILE
from db.database import init_db
from services.user_service import UserService
from services.reminder_service import ReminderService
from utils.storage import Storage
from middleware.logging import LoggingMiddleware
from middleware.error_handler import ErrorHandlerMiddleware
from core.logger import setup_logging
from core.service_provider import ServiceProvider

from handlers import (
    phase_router,
    quests_router,
    insight_router,
    reflect_router,
    reminder_router,
    user_router,
    settings_router,
    onboarding_router,
    buttons_router,
    faq_router,
)

# Set up enhanced logging
logger = setup_logging()

# Initialize bot
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Configure storage and dispatcher
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Add middleware
dp.update.middleware(LoggingMiddleware())
dp.update.middleware(ErrorHandlerMiddleware())

# Include all routers
dp.include_router(phase_router)
dp.include_router(quests_router)
dp.include_router(insight_router)
dp.include_router(reflect_router)
dp.include_router(reminder_router)
dp.include_router(user_router)
dp.include_router(settings_router)
dp.include_router(onboarding_router)
dp.include_router(buttons_router)
dp.include_router(faq_router)

# Register services
def setup_services():
    """Register services with the service provider"""
    logger.info("Registering services")
    # Register basic services
    ServiceProvider.register(Storage, lambda: Storage(DATA_FILE))
    
    # This will expand as more services are added

async def reminder_loop(bot: Bot):
    """Background task for sending reminders to users."""
    logger.info("Starting reminder loop")
    storage = Storage(DATA_FILE)
    
    while True:
        try:
            data = storage.read()
            now = datetime.now().strftime("%H:%M")

            for user_id, user_data in data.items():
                if user_data.get("reminder_enabled") and user_data.get("reminder_time") == now:
                    try:
                        await bot.send_message(int(user_id), "🧘 Пора на рефлексию. Напиши /reflect")
                        logger.info(f"Sent reminder to user {user_id}")
                    except Exception as e:
                        logger.error(f"Failed to send reminder to {user_id}: {e}")
        except Exception as e:
            logger.error(f"Error in reminder loop: {e}")
            
        await asyncio.sleep(60)  # Check every minute

async def main():
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Setup services
        setup_services()
        
        # Set up command menu
        await bot.set_my_commands([
            BotCommand(command="help", description="Как пользоваться ботом"),
            BotCommand(command="faq", description="Часто задаваемые вопросы"),
            BotCommand(command="me", description="Мой статус"),
            BotCommand(command="settings", description="Настройки"),
            BotCommand(command="today", description="Что делать сегодня"),
            BotCommand(command="status", description="Посмотреть текущие квесты"),
            BotCommand(command="start_day", description="Выбрать фазу дня"),
            BotCommand(command="add_quest", description="Добавить квест"),
            BotCommand(command="reflect", description="Вечерняя рефлексия"),
            BotCommand(command="reflections", description="Архив рефлексий"),
            BotCommand(command="insight", description="Добавить инсайт"),
            BotCommand(command="thoughts", description="Посмотреть инсайты"),
            BotCommand(command="reminder", description="Установить напоминание"),
            BotCommand(command="delete_quest", description="Удалить квест")
        ])
        
        # Start background tasks
        asyncio.create_task(reminder_loop(bot))
        logger.info("Background tasks started")
        
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
