FROM python:3.10-slim

# Установка Poetry
RUN pip install poetry

# Установка системных зависимостей (если используешь Pillow, matplotlib и пр.)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7 \
    libtiff5 \
    libwebp-dev \
    tcl-dev tk-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libx11-6 \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Переменная окружения
ENV PYTHONPATH="/app"

# Копируем pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock* /app/

# Установка зависимостей
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Копируем весь проект
COPY . /app/

# Команда запуска бота
CMD ["poetry", "run", "python", "bot.py"]
