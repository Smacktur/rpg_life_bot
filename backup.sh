#!/bin/bash

# Скрипт для создания резервной копии базы данных RPG Life Bot
# Использование: ./backup.sh

set -e

# Создание директории для резервных копий
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# Формирование имени файла резервной копии с датой
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/rpg_bot_backup_$TIMESTAMP.sql"

echo "=== Создание резервной копии базы данных ==="

# Создание резервной копии PostgreSQL
echo "Создание дампа базы данных..."
docker-compose exec postgres pg_dump -U rpgbot rpg_bot > $BACKUP_FILE

# Сжимаем резервную копию для экономии места
echo "Сжатие резервной копии..."
gzip $BACKUP_FILE
BACKUP_FILE="$BACKUP_FILE.gz"

echo "======================================="
echo "Резервная копия успешно создана: $BACKUP_FILE"
echo "======================================="

# Опционально - удаление старых резервных копий (старше 30 дней)
find $BACKUP_DIR -name "rpg_bot_backup_*.sql.gz" -type f -mtime +30 -delete

echo "Старые резервные копии (более 30 дней) удалены." 