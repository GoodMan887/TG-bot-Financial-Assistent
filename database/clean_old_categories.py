from datetime import datetime

import psycopg2

from database.connection import connect_db


def delete_old_deleted_categories():
    """
    Выполняет физическое удаление старых "мягко" удаленных категорий
    и связанных с ними расходов из базы данных.
    Категория считается старой, если она была помечена как удаленная более 30 дней назад.

    Эта функция предназначена для запуска по расписанию (например, в отдельном потоке).
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Нет соединения с БД для очистки.")
        return

    try:
        with conn.cursor() as cur:
            # 1. Удаление всех записей о расходах (expenses),
            # которые связаны с категориями, помеченными как удаленные
            # более 30 дней назад.
            print("Поиск и удаление старых расходов, связанных с удаленными категориями...")
            cur.execute("""
                DELETE FROM expenses
                WHERE category_id IN (
                    SELECT id FROM categories
                    WHERE is_deleted = TRUE
                      AND deleted_at IS NOT NULL
                      AND deleted_at < NOW() - INTERVAL '30 days'
                );
            """)
            print(f"Удалено расходов: {cur.rowcount}") # Логирование количества удаленных строк

            # 2. Физическое удаление самих категорий, которые были "мягко" удалены
            # более 30 дней назад.
            print("Поиск и удаление старых удаленных категорий...")
            cur.execute("""
                DELETE FROM categories
                WHERE is_deleted = TRUE
                  AND deleted_at IS NOT NULL
                  AND deleted_at < NOW() - INTERVAL '30 days';
            """)
            print(f"Удалено категорий: {cur.rowcount}") # Логирование количества удаленных строк

        conn.commit() # Фиксация всех изменений в базе данных
        print(f"[{datetime.now()}] Ежемесячная очистка старых удалённых категорий и их расходов завершена успешно.")
    except psycopg2.Error as e:
        print(f"Ошибка БД при очистке: {e}")
        conn.rollback() # Откат транзакции, если произошла ошибка
    except Exception as e:
        print(f"Неизвестная ошибка при очистке: {e}")
        conn.rollback()
    finally:
        conn.close()
