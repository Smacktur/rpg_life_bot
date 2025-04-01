from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.phase import handle_start_day
from utils.keyboards import main_keyboard

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    text = (
        "🎮 <b>Добро пожаловать в RPG-жизнь</b>\n\n"
        "Этот бот — твоя ролевая система развития. Он помогает:\n"
        "• Определять свою фазу\n"
        "• Планировать день как квест\n"
        "• Фиксировать важные мысли\n"
        "• Рефлексировать каждый вечер\n\n"
        "Готов начать путь?"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Начать", callback_data="onboarding_start_day")
    await message.answer(text, reply_markup=kb.as_markup())
    await message.answer("📋 Главное меню доступно ниже:", reply_markup=main_keyboard)

@router.callback_query(F.data == "onboarding_start_day")
async def onboarding_start(callback: CallbackQuery):
    await callback.message.delete()
    await handle_start_day(callback.message)
    await callback.answer()
