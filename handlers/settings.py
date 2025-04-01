from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pathlib import Path
import json

router = Router()
DATA_FILE = Path("storage/data.json")

@router.message(F.text == "/settings")
async def show_settings(message: Message):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="🧨 Удалить все данные", callback_data="reset_confirm"
        )
    )
    await message.answer("⚙️ <b>Настройки</b>", reply_markup=kb.as_markup())

@router.callback_query(F.data == "reset_confirm")
async def confirm_reset(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_reset"),
        InlineKeyboardButton(text="🔥 Удалить всё", callback_data="reset_all")
    )
    await callback.message.edit_text(
        "🚨 Ты точно хочешь удалить <b>все</b> свои данные? Это <u>безвозвратно</u>.",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_reset")
async def cancel_reset(callback: CallbackQuery):
    await callback.message.edit_text("✅ Отмена. Данные не тронуты.")
    await callback.answer()

@router.callback_query(F.data == "reset_all")
async def reset_all(callback: CallbackQuery):
    user_id = str(callback.from_user.id)

    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        if user_id in data:
            del data[user_id]
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)

    await callback.message.edit_text("🧹 Все данные удалены. Можно начинать с чистого листа.")
    await callback.answer("Данные очищены", show_alert=True)

async def handle_settings(message: Message):
    await show_settings(message)