#!/bin/bash

# Скрипт для развертывания RPG Life Bot на новом сервере
# Использование: ./deploy.sh <bot_token>

set -e

# Проверка передачи токена бота
if [ -z "$1" ]; then
    echo "Ошибка: Не указан токен бота."
    echo "Использование: ./deploy.sh <bot_token>"
    exit 1
fi

BOT_TOKEN=$1

# Проверка наличия Docker и Docker Compose
echo "Проверка зависимостей..."
if ! command -v docker &> /dev/null; then
    echo "Docker не установлен. Устанавливаем..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose не установлен. Устанавливаем..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Создание .env файла с настройками
echo "Создание .env файла..."
cat > .env << EOF
BOT_TOKEN=$BOT_TOKEN
DB_USER=rpgbot
DB_PASSWORD=elmir012
DB_NAME=rpg_bot
REDIS_HOST=redis
REDIS_PORT=6379
USE_SQLITE=false
EOF

# Сборка образа
echo "Сборка Docker-образа..."
docker compose build rpg_bot

# Запуск приложения в Docker
echo "Запуск базы данных и Redis..."
docker compose up -d postgres redis
echo "Ждем 10 секунд, пока PostgreSQL полностью загрузится..."
sleep 10

# Выполнение миграций Alembic
echo "Запуск миграций..."
docker compose run --rm rpg_bot poetry run python -m alembic upgrade head

# Запуск бота
echo "Запуск бота..."
docker compose up -d rpg_bot

echo "======================================"
echo "Развертывание успешно завершено!"
echo "RPG Life Bot запущен в фоновом режиме."
echo "======================================"
echo "Для просмотра логов используйте: docker-compose logs -f rpg_bot"
echo "Для остановки: docker-compose down" 