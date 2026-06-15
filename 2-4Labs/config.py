# config.py - читаю настройки из ENV
# Так мы не храним пароли и чувствительные данные в коде.

import os
from dotenv import load_dotenv

# загружаю переменные из .env файла
load_dotenv()

# настройки базы данных
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "AP080905!@#")
DB_NAME = os.getenv("DB_NAME", "todo_list_db")

# строка подключения
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
