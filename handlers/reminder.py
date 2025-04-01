from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pathlib import Path
from datetime import datetime
import json
import re

router = Router()
DATA_FILE = Path("storage/data.json")


class ReminderState(StatesGroup):
    waiting_for_time = State()


@router.message(F.text == "/reminder")
async def handle_reminder(message: Message):
    user_id = str(message.from_user.id)

    if not DATA_FILE.exists():
        data = {}
    else:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

    user_data = data.get(user_id, {})
    enabled = user_data.get("reminder_enabled", False)
    time = user_data.get("reminder_time", "21:00")

    text = (
        f"🔔 Напоминание о рефлексии: {'включено' if enabled else 'выключено'}\n"
        f"⏰ Время: {time}\n\n"
        f"Выбери действие:"
    )

    kb = InlineKeyboardBuilder()
    kb.button(
        text="❌ Выключить" if enabled else "✅ Включить",
        callback_data="reminder_toggle"
    )
    kb.button(text="⏱ Изменить время", callback_data="reminder_set_time")
    kb.adjust(1)

    await message.answer(text, reply_markup=kb.as_markup())


@router.callback_query(F.data == "reminder_toggle")
async def reminder_toggle(callback: CallbackQuery):
    user_id = str(callback.from_user.id)

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    user_data = data.setdefault(user_id, {})
    current = user_data.get("reminder_enabled", False)
    user_data["reminder_enabled"] = not current

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    status = "включено" if user_data["reminder_enabled"] else "отключено"
    await callback.message.answer(f"🔔 Напоминание {status}.")
    await callback.answer()


@router.callback_query(F.data == "reminder_set_time")
async def reminder_set_time(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReminderState.waiting_for_time)
    await callback.message.answer("🕒 Напиши новое время в формате HH:MM (например, 22:30):")
    await callback.answer()


@router.message(ReminderState.waiting_for_time)
async def set_custom_time(message: Message, state: FSMContext):
    time_text = message.text.strip()
    if not re.match(r"^\d{2}:\d{2}$", time_text):
        await message.answer("⛔ Неверный формат. Пример: 21:45")
        return

    user_id = str(message.from_user.id)
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    user_data = data.setdefault(user_id, {})
    user_data["reminder_time"] = time_text
    data[user_id] = user_data

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    await message.answer(f"✅ Время напоминания установлено: {time_text}")
    await state.clear()

    # Повторный вызов основного меню
    await handle_reminder(message)
