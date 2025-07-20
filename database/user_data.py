from database.connection import connect_db
import psycopg2


def add_or_update_user(telegram_id: int, username: str | None, first_name: str | None, last_name: str | None) -> None:
    """
    Добавляет нового пользователя в базу данных или обновляет существующего,
    если пользователь с таким telegram_id уже есть.

    Args:
        telegram_id (int): Уникальный Telegram ID пользователя.
        username (str | None): Юзернейм пользователя в Telegram. Может быть None.
        first_name (str | None): Имя пользователя в Telegram. Может быть None.
        last_name (str | None): Фамилия пользователя в Telegram. Может быть None.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return

    try:
        with conn.cursor() as cur:
            # SQL-запрос для вставки или обновления пользователя.
            # ON CONFLICT (telegram_id) DO UPDATE SET ...:
            # Если запись с таким telegram_id уже существует, она будет обновлена
            # значениями из EXCLUDED (новыми значениями, которые пытались вставить).
            cur.execute("""
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (telegram_id) DO UPDATE
            SET username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name;
            """, (telegram_id, username, first_name, last_name))
            conn.commit()  # Фиксация изменений в базе данных
    except psycopg2.Error as e:
        print(f"Ошибка БД при добавлении/обновлении пользователя: {e}")
        if conn:
            conn.rollback()  # Откат транзакции
    except Exception as e:
        print(f"Неизвестная ошибка при добавлении/обновлении пользователя: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def find_user_id_by_telegram_id(telegram_id: int) -> int | None:
    """
    Находит внутренний ID пользователя в базе данных по его Telegram ID.

    Args:
        telegram_id (int): Telegram ID пользователя.

    Returns:
        int | None: Внутренний ID пользователя, если найден, иначе None.
                    Возвращает None также в случае ошибки подключения к БД или выполнения запроса.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return None

    user_id = None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM users
                WHERE telegram_id = %s
            """, (telegram_id,))

            result = cur.fetchone()
            if result:
                user_id = result[0]
    except psycopg2.Error as e:
        print(f"Ошибка БД при поиске пользователя по telegram_id: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка при поиске пользователя по telegram_id: {e}")
        return None
    finally:
        if conn:
            conn.close()
    return user_id


def get_user_categories_names_and_ids(user_id: int):
    """
    Получает список всех активных категорий (ID и название) для заданного пользователя.
    Используется для генерации инлайн-кнопок.

    Args:
        user_id (int): ID пользователя, чьи категории нужно получить.

    Returns:
        list[dict]: Список словарей, где каждый словарь содержит 'id' и 'name' категории.
                    Пример: [{'id': 1, 'name': 'Еда'}, {'id': 2, 'name': 'Транспорт'}].
                    Возвращает пустой список в случае ошибки или отсутствия категорий.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return []

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name FROM categories
                WHERE user_id = %s AND is_deleted = FALSE
            """, (user_id,))
            res = cur.fetchall()

            categories_list = []
            for row in res:
                category_id, category_name = row
                categories_list.append({'id': category_id, 'name': category_name})

            return categories_list
    except psycopg2.Error as e:
        print(f"Ошибка БД при поиске категорий пользователя: {e}")
        return []
    except Exception as e:
        print(f"Неизвестная ошибка при поиске категорий пользователя: {e}")
        return []
    finally:
        if conn:
            conn.close()
