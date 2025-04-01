FROM python:3.12-slim

# Установка Poetry
# Лучше использовать рекомендованный способ установки, чтобы избежать потенциальных конфликтов
ENV POETRY_VERSION=1.8.3
RUN pip install "poetry==$POETRY_VERSION"

# Установка системных зависимостей
# Объединяем команды apt-get для уменьшения слоев и размера образа
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    # python3-dev уже есть в базовом образе python
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    # git нужен только если зависимости тянутся из git-репозиториев, иначе можно убрать
    # git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /rpg_bot
# ENV PYTHONPATH не нужен при использовании `poetry run` и стандартной структуре

# Копируем файлы для установки зависимостей
# Это позволяет Docker кэшировать слой установки зависимостей,
# если эти файлы не менялись
COPY pyproject.toml poetry.lock* ./

# Конфигурируем Poetry и устанавливаем ТОЛЬКО зависимости
# Добавляем флаг --no-root
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Копируем оставшийся код проекта
# Этот слой будет пересобираться чаще, т.к. код меняется
COPY . .

# Стартуем бота через poetry run
# Это гарантирует, что зависимости будут доступны
CMD ["python", "bot.py"]