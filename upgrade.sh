#!/bin/bash

# Скрипт для обновления RPG Life Bot на существующем сервере
# Использование: ./upgrade.sh

set -e

echo "=== Обновление RPG Life Bot ==="

# Получение последних изменений
echo "Получение последних изменений из репозитория..."
git pull

# Остановка текущих контейнеров
echo "Остановка текущих контейнеров..."
docker compose down

# Пересборка контейнеров
echo "Пересборка контейнеров..."
docker compose build rpg_bot

# Запуск базы данных и Redis
echo "Запуск базы данных и Redis..."
docker-compose up -d postgres redis
echo "Ждем 5 секунд, пока PostgreSQL полностью загрузится..."
sleep 5

# Выполнение миграций
echo "Запуск миграций..."
docker compose run --rm rpg_bot poetry run python -m alembic upgrade head

# Запуск бота
echo "Запуск бота..."
docker compose up -d rpg_bot

echo "==============================="
echo "Обновление успешно завершено!"
echo "RPG Life Bot перезапущен."
echo "==============================="
echo "Для просмотра логов используйте: docker compose logs -f rpg_bot" 