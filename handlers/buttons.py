from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.insight import handle_insight
from handlers.reflect import handle_reflect_start
from handlers.phase import handle_start_day
from handlers.quests import start_add_quest, handle_status, handle_done, handle_delete_quest
from handlers.user import show_status, render_today_message, help_cmd
from handlers.settings import show_settings
import logging

router = Router()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Мой статус")],
        [KeyboardButton(text="🎯 Сегодня"), KeyboardButton(text="➕ Новый квест")],
        [KeyboardButton(text="🎯 Фокус"), KeyboardButton(text="📋 Квесты")],
        [KeyboardButton(text="✅ Завершить квест"), KeyboardButton(text="🗑️ Удалить квест")],
        [KeyboardButton(text="🕯 Рефлексия"), KeyboardButton(text="🧠 Инсайт")],
        [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие ↓"
)

@router.message(F.text == "/buttons")
async def show_buttons(message: Message):
    await message.answer("Выбери действие:", reply_markup=keyboard)

@router.message(F.text == "/faq")
async def handle_faq_command(message: Message):
    from handlers.faq import faq_intro
    await faq_intro(message)

@router.message()
async def handle_keyboard_button(message: Message, state: FSMContext):
    text = message.text.strip()

    if "Мой статус" in text:
        await show_status(message)

    elif "Сегодня" in text:
        await handle_start_day(message)

    elif "Фокус" in text:
        text = render_today_message(str(message.from_user.id))
        await message.answer(text)

    elif "Квесты" in text:
        await handle_status(message)

    elif "Новый квест" in text:
        await start_add_quest(message, state)

    elif "Завершить" in text:
        await handle_done(message)

    elif "Инсайт" in text:
        await handle_insight(message, state)

    elif "Рефлексия" in text:
        await handle_reflect_start(message, state)

    elif "Настройки" in text:
        await show_settings(message)

    elif "Помощь" in text:
        await help_cmd(message)

    elif "Удалить квест" in text:
        await handle_delete_quest(message)

# Отмена через inline кнопки
@router.callback_query(F.data == "cancel_insight")
async def handle_cancel_insight(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Добавление инсайта отменено.")
    await callback.answer()

@router.callback_query(F.data == "cancel_reflect")
async def handle_cancel_reflect(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Рефлексия отменена.")
    await callback.answer()
