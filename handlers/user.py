from aiogram import Router, F
from aiogram.types import Message
import json
from utils.quest_logic import get_quest_by_phase
from pathlib import Path
from datetime import datetime

router = Router()
DATA_FILE = Path("storage/data.json")

PHASE_LABELS = {
    "active": "⚡ Актива",
    "low": "🌀 Спад",
    "fog": "😵 Подвис"
}

async def show_status(message: Message):
    user_id = str(message.from_user.id)

    if not DATA_FILE.exists():
        await message.answer("Нет данных. Начни с /start_day")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    user_data = data.get(user_id, {})

    phase = user_data.get("phase")
    quests = user_data.get("quests", [])
    insights = user_data.get("insights", [])
    reflections = user_data.get("reflections", [])

    # --- Обработка последней активности ---
    last_active = user_data.get("last_active", {})
    print(f"[DEBUG] last_active raw: {json.dumps(last_active, indent=2)}")
    raw_ts = last_active.get("timestamp")

    # Обработка timestamp
    timestamp = last_active.get("date", "—")

    context = last_active.get("context", "—")
    last_phase = last_active.get("phase", None)
    last_phase_label = PHASE_LABELS.get(last_phase, last_phase.upper()) if last_phase else "—"


    # Обработка фаз
    phase_label = PHASE_LABELS.get(phase, phase.upper()) if phase else "—"
    last_phase_label = PHASE_LABELS.get(last_phase, last_phase.upper()) if last_phase else "—"

    # Подсчёты
    active_quests = [q for q in quests if q.get("status") == "todo"]
    done_quests = [q for q in quests if q.get("status") == "done"]

    text = (
        "👤 <b>Твой статус</b>\n\n"
        f"🌗 Фаза: <b>{phase_label}</b>\n"
        f"📋 Квесты: <b>{len(active_quests)}</b> активных / <b>{len(done_quests)}</b> завершён\n"
        f"🧠 Инсайты: <b>{len(insights)}</b>\n"
        f"🕯 Рефлексии: <b>{len(reflections)}</b>\n\n"
        f"📅 Последняя активность:\n"
        f"<b>{timestamp}</b> — <i>{context}</i> ({last_phase_label})"
    )

    await message.answer(text)


@router.message(F.text == "/help")
async def help_cmd(message: Message):
    await message.answer(
        "Этот бот — твоя ролевая система развития.\n"
        "Он помогает тебе осознанно проживать дни, двигаться к целям, замечать свои фазы и фиксировать инсайты, чтобы ты не терял себя в потоке задач.\n\n"
        "🧭 <b>Как работать с ботом</b>\n\n"
        "1️⃣ <b>Каждое утро</b> — /start_day\n"
        "  • Определи свою фазу: ⚡ Актива / 🌀 Спад / 😵 Подвис\n\n"
        "2️⃣ <b>Добавь квесты</b> — /add_quest\n"
        "  • Это задачи на день / шаги к целям\n\n"
        "3️⃣ <b>Проверь статус</b> — /status\n"
        "  • Посмотри, что осталось\n"
        "  • Заверши задачи — /done (через кнопки)\n\n"
        "4️⃣ <b>Записывай инсайты</b> — /insight\n"
        "  • Мысли, наблюдения, идеи\n"
        "  • Смотри их потом — /thoughts\n\n"
        "5️⃣ <b>Вечером — рефлексия</b> — /reflect\n"
        "  • 3 вопроса: что было важным, что сработало, что изменить\n"
        "  • Смотри архив — /reflections\n\n"
        "6️⃣ <b>Навигация</b>\n"
        "  • /today — Что делать сегодня по фазе\n"
        "  • /me — Сводка по тебе\n"
        "  • /reminder — Настрой напоминания о рефлексии\n\n"
        "📌 Команды всегда доступны через /"
    )

@router.message(F.text == "/today")
async def handle_today(message: Message):
    text = render_today_message(str(message.from_user.id))
    await message.answer(text)

def render_today_message(user_id: str) -> str:
    if not DATA_FILE.exists():
        return "Нет данных. Начни с /start_day"

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    user_data = data.get(user_id, {})
    phase = user_data.get("phase")
    quests = user_data.get("quests", [])

    if not phase:
        return "Фаза не установлена. Напиши /start_day"

    pending = [q for q in quests if q.get("status") == "todo"]
    main_quest = pending[0]["text"] if pending else "Нет активных задач. Добавь через /add_quest"
    tip = get_quest_by_phase(phase)

    return (
        f"📅 <b>Сегодняшний фокус</b>\n\n"
        f"🌗 Фаза: <b>{PHASE_LABELS.get(phase, phase.upper())}</b>\n\n"
        f"🎯 Главная задача: <b>{main_quest}</b>\n\n"
        f"💡 Совет на фазу:\n{tip}"
    )