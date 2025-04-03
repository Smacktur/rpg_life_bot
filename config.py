import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    # Просто выводим предупреждение вместо исключения для запуска миграций
    print("WARNING: BOT_TOKEN environment variable is not set")
    BOT_TOKEN = "dummy_token_for_migrations"

# Database settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "rpg_bot")

# SQLite path for local development
SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rpg_bot.db")

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Create database URL
def get_database_url(use_sqlite=False) -> str:
    """Get database URL
    
    Args:
        use_sqlite: If True, returns SQLite URL instead of PostgreSQL
        
    Returns:
        Database connection URL
    """
    if use_sqlite:
        return f"sqlite+aiosqlite:///{SQLITE_PATH}"
    return f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Sync database URL for migrations
def get_sync_database_url(use_sqlite=False) -> str:
    """Get synchronous database URL for migrations
    
    Args:
        use_sqlite: If True, returns SQLite URL instead of PostgreSQL
        
    Returns:
        Synchronous database connection URL
    """
    if use_sqlite:
        return f"sqlite:///{SQLITE_PATH}"
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Other settings
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage")
DATA_FILE = os.path.join(DATA_DIR, "data.json") 