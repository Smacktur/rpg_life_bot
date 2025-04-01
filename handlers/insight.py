from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from pathlib import Path
from utils.helpers import update_last_active
import json

router = Router()
DATA_FILE = Path("storage/data.json")

class InsightState(StatesGroup):
    waiting = State()

markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_insight")]
])

@router.message(F.text == "/insight")
async def handle_insight(message: Message, state: FSMContext):
    await message.answer(
        "🧠 <b>Поймал инсайт?</b>\n\n"
        "Инсайт — это момент, когда ты:\n"
        "• понял что-то важное о себе или мире\n"
        "• почувствовал 'щёлкнуло'\n"
        "• увидел закономерность или причину\n\n"
        "<b>Формула:</b>\n"
        "1. Что увидел (наблюдение)\n"
        "2. Что понял (вывод)\n"
        "3. Что это меняет для тебя\n\n"
        "<b>Примеры:</b>\n"
        "• Когда я не высыпаюсь — мне сложнее говорить «нет»\n"
        "• Я тяну с задачей не потому, что лень, а потому что боюсь облажаться\n"
        "• Мне важно быть не правым, а принятым — и это мешает в спорах\n\n"
        "📝 Напиши свой инсайт:",
        reply_markup=markup
    )
    await state.set_state(InsightState.waiting)

@router.message(InsightState.waiting)
async def save_insight(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    insight = message.text.strip()

    if not DATA_FILE.exists():
        data = {}
    else:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

    user_data = data.get(user_id, {})
    insights = user_data.get("insights", [])

    update_last_active(user_data, context="insight", phase=user_data.get("phase"))

    insights.append({
        "text": insight,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    user_data["insights"] = insights
    data[user_id] = user_data

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    await message.answer("✅ Инсайт сохранён.")
    await state.clear()

@router.message(F.text == "/thoughts")
async def handle_thoughts(message: Message):
    user_id = str(message.from_user.id)

    if not DATA_FILE.exists():
        await message.answer("🧠 Мысли не найдены.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    insights = data.get(user_id, {}).get("insights", [])

    if not insights:
        await message.answer("Пока нет ни одного инсайта.")
        return

    await show_insight(message, insights, 0)

async def show_insight(target, insights, index: int):
    insight = insights[index]
    total = len(insights)
    text = (
        f"🧠 <b>Инсайт #{index + 1} из {total}</b>\n\n"
        f"{insight.get('text')}\n\n"
        f"🕒 {insight.get('date', '-') }"
    )

    kb = InlineKeyboardBuilder()
    prev_index = (index - 1) % total
    next_index = (index + 1) % total

    kb.row(
        InlineKeyboardButton(text="⬅️", callback_data=f"insight_nav_{prev_index}"),
        InlineKeyboardButton(text="🗑️", callback_data=f"insight_delete_{index}"),
        InlineKeyboardButton(text="➡️", callback_data=f"insight_nav_{next_index}")
    )

    if isinstance(target, Message):
        await target.answer(text, reply_markup=kb.as_markup())
    elif isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(text, reply_markup=kb.as_markup())
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                await target.answer("📌 Это уже текущая запись.")
            else:
                raise e
        else:
            await target.answer()

@router.callback_query(F.data.startswith("insight_nav_"))
async def handle_insight_navigation(callback: CallbackQuery):
    index = int(callback.data.split("_")[-1])
    user_id = str(callback.from_user.id)

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    insights = data.get(user_id, {}).get("insights", [])
    if not insights:
        await callback.message.edit_text("Нет инсайтов.")
        return

    await show_insight(callback, insights, index)

@router.callback_query(F.data.startswith("insight_delete_"))
async def delete_insight(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    index = int(callback.data.split("_")[-1])

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    insights = data.get(user_id, {}).get("insights", [])

    if index >= len(insights):
        await callback.answer("Неверный индекс.")
        return

    del insights[index]
    data[user_id]["insights"] = insights

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    if not insights:
        await callback.message.edit_text("🧠 Все инсайты удалены.")
        await callback.answer()
        return

    new_index = max(0, index - 1)
    await show_insight(callback, insights, new_index)
    await callback.answer("🗑️ Удалено")