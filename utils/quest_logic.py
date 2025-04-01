def get_quest_by_phase(phase: str) -> str:
    if phase == "active":
        return "Выбери 1 задачу из backlog и сделай её до конца 💪"
    elif phase == "low":
        return "Напиши 1 мысль или идею, просто чтобы сохранить контакт с собой 🧘"
    elif phase == "fog":
        return "Открой Obsidian, запиши 1 строчку: 'Что я сейчас чувствую?'" 
    else:
        return "Неопознанная фаза. Ты вне времени и пространства 👽"
