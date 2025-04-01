from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.quest_logic import get_quest_by_phase
from utils.helpers import update_last_active
from aiogram.filters import Command
import json
from pathlib import Path
import logging

router = Router()
logger = logging.getLogger(__name__)
DATA_FILE = Path("storage/data.json")

PHASE_LABELS = {
    "active": "⚡ Актива",
    "low": "🌀 Спад",
    "fog": "😵 Подвис"
}

def save_phase(user_id: int, phase: str):
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    user_id = str(user_id)
    user_data = data.get(user_id, {})
    user_data["phase"] = phase
    update_last_active(user_data, context="phase", phase=phase)
    data[user_id] = user_data

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@router.message(F.text == "/start_day")
async def handle_start_day(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="⚡ Актива", callback_data="phase_active")
    builder.button(text="🌀 Спад", callback_data="phase_low")
    builder.button(text="😵 Подвис", callback_data="phase_fog")
    builder.adjust(1)
    await message.answer("В какой ты фазе?", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("phase_"))
async def handle_phase(callback: CallbackQuery):
    phase = callback.data.split("_")[1]
    user_id = callback.from_user.id
    save_phase(user_id, phase)
    quest = get_quest_by_phase(phase)
    label = PHASE_LABELS.get(phase, phase.upper())
    await callback.message.answer(f"🌗 Фаза выбрана: <b>{label}</b>\n\n🎯 Твоя задача:\n{quest}")
    await callback.answer()