"""
Скрипт для миграции данных из JSON в базу данных.
Использование:
    python migrate_data.py
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from datetime import datetime

from db.database import init_db
from db.models import User, Quest, Insight, Reflection, LastActive
from utils.storage import Storage
from config import DATA_FILE
from core.logger import setup_logging

# Настройка логирования
logger = setup_logging()

async def migrate_json_to_db():
    """Миграция данных из JSON в базу данных"""
    logger.info("Starting data migration from JSON to database")
    
    # Проверка наличия JSON-файла
    if not os.path.exists(DATA_FILE):
        logger.warning(f"JSON file {DATA_FILE} not found. Nothing to migrate.")
        return
    
    # Чтение данных из JSON
    storage = Storage(DATA_FILE)
    data = storage.read()
    
    if not data:
        logger.warning("JSON file is empty. Nothing to migrate.")
        return
    
    # Инициализация счетчиков
    users_migrated = 0
    quests_migrated = 0
    insights_migrated = 0
    reflections_migrated = 0
    errors = []
    
    # Импорт сессии здесь для избежания циклических импортов
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    from db.database import engine
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Обработка каждого пользователя
        for user_id, user_data in data.items():
            try:
                logger.info(f"Migrating user {user_id}")
                
                # Создание или обновление пользователя
                user = User(
                    telegram_id=user_id,
                    phase=user_data.get("phase"),
                    reminder_enabled=user_data.get("reminder_enabled", False),
                    reminder_time=user_data.get("reminder_time"),
                    created_at=datetime.now()
                )
                session.add(user)
                await session.flush()  # Получение ID пользователя
                users_migrated += 1
                
                # Миграция квестов
                quests = user_data.get("quests", [])
                for quest_data in quests:
                    quest = Quest(
                        user_id=user.id,
                        text=quest_data.get("text", ""),
                        status=quest_data.get("status", "todo"),
                        phase=quest_data.get("phase"),
                        created_at=datetime.now()
                    )
                    session.add(quest)
                    quests_migrated += 1
                
                # Миграция инсайтов
                insights = user_data.get("insights", [])
                for insight_data in insights:
                    if isinstance(insight_data, dict):
                        text = insight_data.get("text", "")
                    elif isinstance(insight_data, str):
                        text = insight_data
                    else:
                        continue
                        
                    insight = Insight(
                        user_id=user.id,
                        text=text,
                        created_at=datetime.now()
                    )
                    session.add(insight)
                    insights_migrated += 1
                
                # Миграция рефлексий
                reflections = user_data.get("reflections", [])
                for reflection_data in reflections:
                    reflection = Reflection(
                        user_id=user.id,
                        important=reflection_data.get("important", ""),
                        worked=reflection_data.get("worked", ""),
                        change=reflection_data.get("change", ""),
                        created_at=datetime.now()
                    )
                    session.add(reflection)
                    reflections_migrated += 1
                
                # Миграция последней активности
                last_active_data = user_data.get("last_active")
                if last_active_data:
                    last_active = LastActive(
                        user_id=user.id,
                        timestamp=datetime.now(),
                        context=last_active_data.get("context", ""),
                        phase=last_active_data.get("phase")
                    )
                    session.add(last_active)
                
            except Exception as e:
                logger.error(f"Error migrating user {user_id}: {e}")
                errors.append(f"User {user_id}: {str(e)}")
                
        # Сохранение изменений
        try:
            await session.commit()
            logger.info("All changes committed to database")
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            await session.rollback()
            errors.append(f"Commit error: {str(e)}")
            
    # Итоги миграции
    logger.info(f"Migration completed:")
    logger.info(f"- Users migrated: {users_migrated}")
    logger.info(f"- Quests migrated: {quests_migrated}")
    logger.info(f"- Insights migrated: {insights_migrated}")
    logger.info(f"- Reflections migrated: {reflections_migrated}")
    
    if errors:
        logger.warning(f"There were {len(errors)} errors during migration:")
        for error in errors:
            logger.warning(f"- {error}")
    
    return {
        "users_migrated": users_migrated,
        "quests_migrated": quests_migrated,
        "insights_migrated": insights_migrated,
        "reflections_migrated": reflections_migrated,
        "errors": errors
    }

async def main():
    """Основная функция"""
    # Инициализация базы данных
    await init_db()
    
    # Миграция данных
    result = await migrate_json_to_db()
    
    # Создание резервной копии JSON-файла
    if os.path.exists(DATA_FILE):
        backup_file = f"{DATA_FILE}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            os.rename(DATA_FILE, backup_file)
            logger.info(f"Created backup of JSON file: {backup_file}")
        except Exception as e:
            logger.error(f"Error creating backup: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 