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
    logging.info(f"[BUTTONS] Получено сообщение: {text!r}")

    if "Мой статус" in text:
        logging.info("[BUTTONS] Вызов: СТАТУС")
        await show_status(message)

    elif "Сегодня" in text:
        logging.info("[BUTTONS] Вызов: СЕГОДНЯ")
        await handle_start_day(message)

    elif "Фокус" in text:
        logging.info("[BUTTONS] Вызов: TODAY")
        text = render_today_message(str(message.from_user.id))
        await message.answer(text)

    elif "Квесты" in text:
        logging.info("[BUTTONS] Вызов: КВЕСТЫ")
        await handle_status(message)

    elif "Новый квест" in text:
        logging.info("[BUTTONS] Вызов: НОВЫЙ КВЕСТ")
        await start_add_quest(message, state)

    elif "Завершить" in text:
        logging.info("[BUTTONS] Вызов: ЗАВЕРШИТЬ КВЕСТ")
        await handle_done(message)

    elif "Инсайт" in text:
        logging.info("[BUTTONS] Вызов: ИНСАЙТ")
        await handle_insight(message, state)

    elif "Рефлексия" in text:
        logging.info("[BUTTONS] Вызов: РЕФЛЕКСИЯ")
        await handle_reflect_start(message, state)

    elif "Настройки" in text:
        logging.info("[BUTTONS] Вызов: НАСТРОЙКИ")
        await show_settings(message)

    elif "Помощь" in text:
        logging.info("[BUTTONS] Вызов: HELP")
        await help_cmd(message)

    elif "Удалить квест" in text:
        logging.info("[BUTTONS] Вызов: УДАЛИТЬ КВЕСТ")
        await handle_delete_quest(message)

    else:
        logging.info("[BUTTONS] Неизвестная команда")

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
