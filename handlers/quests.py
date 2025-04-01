from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from datetime import datetime
from pathlib import Path
import json

from utils.helpers import update_last_active
from utils.quest_logic import get_quest_by_phase

router = Router()
DATA_FILE = Path("storage/data.json")

class QuestStates(StatesGroup):
    waiting_for_text = State()

def get_next_id(quests):
    if not quests:
        return 1
    return max(q["id"] for q in quests) + 1

@router.message(Command("add_quest"))
async def start_add_quest(message: Message, state: FSMContext):
    await message.answer("📝 Напиши квест:")
    await state.set_state(QuestStates.waiting_for_text)

@router.message(F.text == "➕ Новый квест")
async def start_add_quest_button(message: Message, state: FSMContext):
    await start_add_quest(message, state)

@router.message(QuestStates.waiting_for_text)
async def save_quest(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    quest = message.text.strip()

    if not quest:
        await message.answer("⛔️ Квест не может быть пустым.")
        return

    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    user_data = data.get(user_id, {})
    quests = user_data.get("quests", [])
    phase = user_data.get("phase")
    update_last_active(user_data, context="quest", phase=phase)

    # 🔥 проверка соответствия фазе
    phase_tip = get_quest_by_phase(phase) if phase else None
    if phase and phase_tip and not any(kw.lower() in quest.lower() for kw in phase_tip.lower().split()):
        await message.answer(f"⚠️ Этот квест может не соответствовать текущей фазе: <b>{phase.upper()}</b>\n💡 Рекомендация: {phase_tip}")

    new_id = get_next_id(quests)
    quests.append({
        "id": new_id,
        "text": quest,
        "status": "todo",
        "phase": phase
    })
    user_data["quests"] = quests
    data[user_id] = user_data

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    await state.clear()
    await message.answer("✅ Квест добавлен!", show_alert=True)
    await handle_status(message)

@router.message(Command("status"))
async def handle_status(message: Message):
    user_id = str(message.from_user.id)

    if not DATA_FILE.exists():
        await message.answer("У тебя пока нет квестов.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    user_data = data.get(user_id, {})
    quests = user_data.get("quests", [])

    if not quests:
        await message.answer("У тебя пока нет квестов.")
        return

    lines = ["📋 <b>Твои квесты:</b>\n"]
    keyboard = InlineKeyboardBuilder()

    for q in quests:
        status_icon = "✅" if q.get("status") == "done" else "🕒"
        phase_note = f" ({q.get('phase')})" if q.get("phase") else ""
        lines.append(f"{status_icon} <b>{q['id']}</b>: {q['text']}{phase_note}")
        if q.get("status") != "done":
            keyboard.button(
                text=f"✅ Завершить: {q['text'][:20]}",
                callback_data=f"inline_done_{q['id']}"
            )

    keyboard.adjust(1)
    await message.answer("\n".join(lines), reply_markup=keyboard.as_markup())

@router.callback_query(F.data.startswith("inline_done_"))
async def handle_inline_done(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    quest_id = int(callback.data.split("_")[-1])

    if not DATA_FILE.exists():
        await callback.answer("Нет данных.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    user_data = data.get(user_id, {})
    quests = user_data.get("quests", [])

    for q in quests:
        if q["id"] == quest_id:
            q["status"] = "done"
            update_last_active(user_data, context="quest_done", phase=user_data.get("phase"))
            break
    else:
        await callback.answer("⛔️ Квест не найден или уже выполнен.")
        return

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    lines = ["📋 <b>Твои квесты:</b>\n"]
    keyboard = InlineKeyboardBuilder()
    for q in quests:
        status_icon = "✅" if q.get("status") == "done" else "🕒"
        phase_note = f" ({q.get('phase')})" if q.get("phase") else ""
        lines.append(f"{status_icon} <b>{q['id']}</b>: {q['text']}{phase_note}")
        if q.get("status") != "done":
            keyboard.button(
                text=f"✅ Завершить: {q['text'][:20]}",
                callback_data=f"inline_done_{q['id']}"
            )
    keyboard.adjust(1)
    await callback.message.edit_text("\n".join(lines), reply_markup=keyboard.as_markup())
    await callback.answer("✅ Квест завершён!", show_alert=True)

@router.message(Command("done"))
async def handle_done(message: Message):
    user_id = str(message.from_user.id)

    if not DATA_FILE.exists():
        await message.answer("У тебя пока нет квестов.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    quests = data.get(user_id, {}).get("quests", [])
    pending = [q for q in quests if q["status"] == "todo"]

    if not pending:
        await message.answer("Нет активных квестов для завершения.")
        return

    keyboard = InlineKeyboardBuilder()
    for q in pending:
        keyboard.button(text=f"{q['id']}: {q['text'][:30]}", callback_data=f"inline_done_{q['id']}")
    keyboard.adjust(1)

    await message.answer("Выбери квест, который выполнил:", reply_markup=keyboard.as_markup())

@router.message(F.text == "/delete_quest")
async def handle_delete_quest(message: Message):
    user_id = str(message.from_user.id)

    if not DATA_FILE.exists():
        await message.answer("Квесты не найдены.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    quests = data.get(user_id, {}).get("quests", [])

    if not quests:
        await message.answer("Пока нет квестов.")
        return

    builder = InlineKeyboardBuilder()
    for q in quests:
        label = f"{q['id']}: {q['text'][:30]}"
        builder.button(text=f"❌ {label}", callback_data=f"del_quest_{q['id']}")
    builder.adjust(1)

    await message.answer("Выбери квест для удаления:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("del_quest_"))
async def delete_quest(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    quest_id = int(callback.data.split("_")[-1])

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    quests = data.get(user_id, {}).get("quests", [])
    quests = [q for q in quests if q["id"] != quest_id]
    data[user_id]["quests"] = quests

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    await callback.message.edit_text("🗑️ Квест удалён.")
    await callback.answer()