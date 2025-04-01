from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime
from pathlib import Path
import json

router = Router()
DATA_FILE = Path("storage/data.json")

class ReflectStates(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()

markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_reflect")]
])

@router.message(F.text == "/reflect")
async def handle_reflect_start(message: Message, state: FSMContext):
    await message.answer("🧘 Что было самым важным сегодня?",
        reply_markup=markup)
    await state.set_state(ReflectStates.q1)

@router.message(ReflectStates.q1)
async def handle_q1(message: Message, state: FSMContext):
    await state.update_data(q1=message.text.strip())
    await message.answer("✅ Что сегодня сработало хорошо?")
    await state.set_state(ReflectStates.q2)

@router.message(ReflectStates.q2)
async def handle_q2(message: Message, state: FSMContext):
    await state.update_data(q2=message.text.strip())
    await message.answer("⚠️ Что бы ты сделал иначе?")
    await state.set_state(ReflectStates.q3)

@router.message(ReflectStates.q3)
async def handle_q3(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    q3 = message.text.strip()
    answers = await state.get_data()

    if not DATA_FILE.exists():
        data = {}
    else:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

    user_data = data.get(user_id, {})
    reflections = user_data.get("reflections", [])

    reflection_entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "q1": answers.get("q1"),
        "q2": answers.get("q2"),
        "q3": q3
    }

    reflections.append(reflection_entry)
    user_data["reflections"] = reflections
    data[user_id] = user_data

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    await message.answer("🧠 Рефлексия сохранена. День закрыт.")
    await state.clear()

@router.message(F.text == "/reflections")
async def reflections_start(message: Message):
    user_id = str(message.from_user.id)
    with open(DATA_FILE) as f:
        data = json.load(f)

    reflections = data.get(user_id, {}).get("reflections", [])
    if not reflections:
        await message.answer("Нет рефлексий.")
        return

    months = sorted(set([r["date"][:7] for r in reflections]), reverse=True)
    kb = InlineKeyboardBuilder()
    for m in months:
        kb.button(text=m, callback_data=f"reflect_month_{m}")
    kb.adjust(2)
    await message.answer("📅 Выбери месяц:", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("reflect_month_"))
async def reflections_select_month(callback: CallbackQuery):
    month = callback.data.split("_")[-1]
    user_id = str(callback.from_user.id)

    with open(DATA_FILE) as f:
        data = json.load(f)

    reflections = data.get(user_id, {}).get("reflections", [])
    dates = [r["date"][:10] for r in reflections if r["date"].startswith(month)]
    unique_dates = sorted(set(dates))
    kb = InlineKeyboardBuilder()
    for d in unique_dates:
        kb.button(text=d, callback_data=f"reflect_view_{d}_0")
    kb.row(InlineKeyboardButton(text="⬅️ Назад к месяцам", callback_data="reflect_back_months"))
    await callback.message.edit_text(f"📅 Записи за {month}:", reply_markup=kb.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("reflect_view_"))
async def reflections_view(callback: CallbackQuery):
    parts = callback.data.split("_")
    date = parts[2]
    index = int(parts[3])
    user_id = str(callback.from_user.id)

    with open(DATA_FILE) as f:
        data = json.load(f)

    all_reflections = data.get(user_id, {}).get("reflections", [])
    day_reflections = [r for r in all_reflections if r["date"].startswith(date)]
    if not day_reflections:
        await callback.answer("Нет записей на эту дату")
        return

    r = day_reflections[index]
    total = len(day_reflections)
    text = (
        f"🪞 <b>Рефлексия #{index + 1} из {total}</b>\n\n"
        f"1. {r['q1']}\n"
        f"2. {r['q2']}\n"
        f"3. {r['q3']}\n\n"
        f"🕒 {r['date']}"
    )

    kb = InlineKeyboardBuilder()
    prev_index = index - 1 if index > 0 else len(day_reflections) - 1
    next_index = (index + 1) % len(day_reflections)

    kb.row(
        InlineKeyboardButton(text="⬅️", callback_data=f"reflect_view_{date}_{prev_index}"),
        InlineKeyboardButton(text="🗑️", callback_data=f"reflect_delete_{date}_{index}"),
        InlineKeyboardButton(text="➡️", callback_data=f"reflect_view_{date}_{next_index}")
    )
    kb.row(InlineKeyboardButton(text="↩️ Назад к датам", callback_data=f"reflect_back_{date[:7]}"))

    try:
        await callback.message.edit_text(text, reply_markup=kb.as_markup())
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("📌 Это уже текущая запись.")
        else:
            raise e
    else:
        await callback.answer()

@router.callback_query(F.data.startswith("reflect_delete_"))
async def reflections_delete(callback: CallbackQuery):
    _, _, date, index = callback.data.split("_")
    index = int(index)
    user_id = str(callback.from_user.id)

    with open(DATA_FILE) as f:
        data = json.load(f)

    reflections = data.get(user_id, {}).get("reflections", [])
    day_entries = [i for i, r in enumerate(reflections) if r["date"].startswith(date)]

    if index >= len(day_entries):
        await callback.answer("Неверный индекс")
        return

    del reflections[day_entries[index]]
    data[user_id]["reflections"] = reflections

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    await callback.message.edit_text("🗑️ Рефлексия удалена.")
    await callback.answer()

@router.callback_query(F.data.startswith("reflect_back_"))
async def reflections_back_to_dates(callback: CallbackQuery):
    month = callback.data.split("_")[-1]
    user_id = str(callback.from_user.id)

    with open(DATA_FILE) as f:
        data = json.load(f)

    reflections = data.get(user_id, {}).get("reflections", [])
    dates = [r["date"][:10] for r in reflections if r["date"].startswith(month)]
    unique_dates = sorted(set(dates))
    if not unique_dates:
        await callback.message.edit_text("Нет записей за этот месяц.")
        return

    kb = InlineKeyboardBuilder()
    for d in unique_dates:
        kb.button(text=d, callback_data=f"reflect_view_{d}_0")
    kb.adjust(3)
    kb.row(InlineKeyboardButton(text="⬅️ Назад к месяцам", callback_data="reflect_back_months"))

    await callback.message.edit_text(f"📅 Записи за {month}:", reply_markup=kb.as_markup())
    await callback.answer()

@router.callback_query(F.data == "reflect_back_months")
async def reflections_back_to_months(callback: CallbackQuery):
    await reflections_start(callback.message)
    await callback.answer()
