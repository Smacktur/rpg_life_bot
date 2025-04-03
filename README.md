# RPG Life Bot

Телеграм-бот для геймификации жизни в RPG-стиле.

## Описание

Этот бот помогает вам:
- Отслеживать свои фазы активности
- Ставить и выполнять квесты (задачи)
- Записывать инсайты 
- Проводить ежедневную рефлексию
- Получать рекомендации в зависимости от вашей фазы

## Технологический стек

- Python 3.12
- Aiogram 3.19
- Docker / Docker Compose
- PostgreSQL
- SQLite (для разработки)
- Redis
- Celery
- Poetry

## Установка

### Используя Poetry (рекомендуется)

1. Клонируйте репозиторий:
   ```bash
   git clone <url-репозитория>
   cd rpg_life_bot
   ```

2. Установите зависимости:
   ```bash
   poetry install
   ```

3. Создайте файл `.env` с конфигурацией:
   ```
   BOT_TOKEN=your_bot_token_here
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=rpg_bot
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

4. Примените миграции к базе данных:
   ```bash
   poetry run alembic upgrade head
   ```

### Используя Docker

1. Клонируйте репозиторий:
   ```bash
   git clone <url-репозитория>
   cd rpg_life_bot
   ```

2. Создайте файл `.env` с конфигурацией:
   ```
   BOT_TOKEN=your_bot_token_here
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=rpg_bot
   ```

3. Запустите проект:
   ```bash
   docker-compose up -d
   ```

## Запуск

### Локально 

Запуск бота:
```bash
poetry run python bot.py
```

Запуск Celery worker для фоновых задач:
```bash
poetry run python run_celery.py worker
```

Запуск Celery beat для периодических задач:
```bash
poetry run python run_celery.py beat
```

Запуск всех компонентов одной командой:
```bash
poetry run python run_celery.py all
```

### В Docker

```bash
docker-compose up -d
```

## Миграция данных из JSON в БД

Если у вас есть данные в формате JSON (storage/data.json), вы можете мигрировать их в базу данных:

```bash
poetry run python migrate_data.py
```

## Разработка

### Создание миграций

При изменении моделей данных необходимо создать и применить миграции:

```bash
# Создание миграции
poetry run alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
poetry run alembic upgrade head
```

### Тестирование

Запуск тестов:

```bash
poetry run pytest
```

## Структура проекта

```
.
├── bot.py            # Основной файл запуска бота
├── config.py         # Конфигурация
├── celery_app.py     # Конфигурация Celery
├── tasks.py          # Асинхронные задачи Celery
├── db/               # Модули для работы с базой данных
│   ├── database.py   # Подключение к БД
│   └── models.py     # ORM модели
├── handlers/         # Обработчики команд и сообщений
├── middleware/       # Промежуточные обработчики
├── migrations/       # Миграции Alembic
├── services/         # Бизнес-логика
├── utils/            # Вспомогательные утилиты
├── tests/            # Тесты
└── storage/          # Хранилище данных
```

## Лицензия

MIT 