import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from pathlib import Path
from aiogram.fsm.storage.memory import MemoryStorage
import json
from datetime import datetime

from config import BOT_TOKEN
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

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

DATA_FILE = Path("storage/data.json")

storage = MemoryStorage()
dp = Dispatcher(storage=MemoryStorage())

# Подключаем все роутеры
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

async def reminder_loop(bot: Bot):
    while True:
        if DATA_FILE.exists():
            with open(DATA_FILE, "r") as f:
                data = json.load(f)

            now = datetime.now().strftime("%H:%M")

            for user_id, user_data in data.items():
                if user_data.get("reminder_enabled") and user_data.get("reminder_time") == now:
                    try:
                        await bot.send_message(int(user_id), "🧘 Пора на рефлексию. Напиши /reflect")
                    except Exception as e:
                        print(f"Failed to send reminder to {user_id}: {e}")

        await asyncio.sleep(60)  # проверяем каждую минуту

async def main():
    # запускаем фоновую задачу с напоминаниями
    asyncio.create_task(reminder_loop(bot))

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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
