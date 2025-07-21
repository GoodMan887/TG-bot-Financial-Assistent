import os

import psycopg2
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()


def connect_db():
    database_url = os.getenv("DB_URL")

    if not database_url:
        raise ValueError("DB_URL environment variable is not set.")

    conn = psycopg2.connect(database_url)
    return conn
