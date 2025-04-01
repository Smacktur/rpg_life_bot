from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎯 Сегодня"), KeyboardButton(text="➕ Новый квест")],
        [KeyboardButton(text="✅ Завершить квест"), KeyboardButton(text="🧠 Инсайт")],
        [KeyboardButton(text="🕯 Рефлексия"), KeyboardButton(text="⚙️ Настройки")]
    ],
    resize_keyboard=True,
    is_persistent=True
)
