import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from celery_app import app
from config import BOT_TOKEN
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

logger = logging.getLogger(__name__)

# Initialize bot instance for tasks
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

@app.task
def check_reminders() -> Dict[str, Any]:
    """
    Celery task to check reminders and send notifications.
    Runs every minute via beat schedule.
    
    Returns:
        Dictionary with task results
    """
    logger.info("Running reminder check")
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        result = loop.run_until_complete(_check_reminders_async())
        return result
    except Exception as e:
        logger.error(f"Error in reminder check: {e}")
        return {"status": "error", "error": str(e)}

async def _check_reminders_async() -> Dict[str, Any]:
    """
    Async function to check reminders and send notifications.
    
    Returns:
        Dictionary with task results
    """
    from services.reminder_service import ReminderService
    
    now = datetime.now().strftime("%H:%M")
    logger.info(f"Checking reminders for time: {now}")
    
    try:
        # Get users with reminders set for now
        users = await ReminderService.get_users_for_reminder(now)
        
        # Send notifications
        sent_count = 0
        error_count = 0
        
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text="🧘 Пора на рефлексию. Напиши /reflect"
                )
                sent_count += 1
                logger.info(f"Sent reminder to user {user.telegram_id}")
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to send reminder to {user.telegram_id}: {e}")
                
        return {
            "status": "success",
            "time": now,
            "users_count": len(users),
            "sent_count": sent_count,
            "error_count": error_count
        }
    except Exception as e:
        logger.error(f"Error processing reminders: {e}")
        return {"status": "error", "error": str(e)}

@app.task
def migrate_legacy_data() -> Dict[str, Any]:
    """
    Celery task to migrate legacy data from JSON to database.
    One-time task that can be triggered manually.
    
    Returns:
        Dictionary with migration results
    """
    logger.info("Starting legacy data migration")
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        result = loop.run_until_complete(_migrate_legacy_data_async())
        return result
    except Exception as e:
        logger.error(f"Error in data migration: {e}")
        return {"status": "error", "error": str(e)}

async def _migrate_legacy_data_async() -> Dict[str, Any]:
    """
    Async function to migrate legacy data from JSON to database.
    
    Returns:
        Dictionary with migration results
    """
    from utils.storage import Storage
    from config import DATA_FILE
    from services.user_service import UserService
    from services.quest_service import QuestService
    
    storage = Storage(DATA_FILE)
    data = storage.read()
    
    users_migrated = 0
    quests_migrated = 0
    insights_migrated = 0
    reflections_migrated = 0
    errors = []
    
    for user_id, user_data in data.items():
        try:
            # Migrate user
            user = await UserService.get_or_create_user(user_id)
            users_migrated += 1
            
            # Update user properties
            if user_data.get("phase"):
                await UserService.update_phase(user_id, user_data["phase"])
                
            # TODO: Implement migration for other data types
                
        except Exception as e:
            errors.append(f"Error migrating user {user_id}: {e}")
            logger.error(f"Error migrating user {user_id}: {e}")
            
    return {
        "status": "success" if not errors else "partial",
        "users_migrated": users_migrated,
        "quests_migrated": quests_migrated,
        "insights_migrated": insights_migrated,
        "reflections_migrated": reflections_migrated,
        "errors": errors if errors else None
    } 