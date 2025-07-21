import psycopg2

from database.connection import connect_db


def get_category_name_by_id(category_id: int) -> str | None:
    """
    Получает название категории по её уникальному ID.

    Args:
        category_id (int): Уникальный идентификатор категории.

    Returns:
        str | None: Название категории, если найдено, иначе None.
                    Возвращает None также в случае ошибки подключения к БД или выполнения запроса.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return None

    try:
        with conn.cursor() as cur:
            # Выполнение SQL-запроса для выбора названия категории по ID
            cur.execute("""
                SELECT name FROM categories
                WHERE id = %s
            """, (category_id,))
            result = cur.fetchone()
            return result[0] if result else None  # Возвращаем название или None, если категория не найдена
    except psycopg2.Error as e:  # Ловим специфическое исключение
        print(f"Ошибка БД при получении названия категории: {e}")
        return None
    except Exception as e:  # Ловим любые другие неожиданные исключения
        print(f"Неизвестная ошибка при получении названия категории: {e}")
        return None
    finally:
        conn.close()


def create_category(user_id: int, category_name: str):
    """
    Создает новую категорию в базе данных.

    Args:
        user_id (int): ID пользователя, которому принадлежит категория.
        category_name (str): Название новой категории.

    Returns:
        bool: True, если категория успешно создана, False в противном случае.
              Возвращает False также в случае ошибки подключения к БД или выполнения запроса.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return False

    try:
        with conn.cursor() as cur:
            # Выполнение SQL-запроса для вставки новой категории
            cur.execute("""
                INSERT INTO categories (user_id, name)
                VALUES (%s, %s)
            """, (user_id, category_name))
            conn.commit()  # Фиксация изменений в базе данных
            return True
    except psycopg2.Error as e:
        print(f"Ошибка БД при создании категории: {e}")
        conn.rollback()  # Откат транзакции в случае ошибки
        return False
    except Exception as e:
        print(f"Неизвестная ошибка при создании категории: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def rename_category_in_db(category_id: int, new_name: str):
    """
    Переименовывает существующую категорию в базе данных.

    Args:
        category_id (int): Уникальный идентификатор категории для переименования.
        new_name (str): Новое название для категории.

    Returns:
        bool: True, если категория успешно переименована, False в противном случае.
              Возвращает False также в случае ошибки подключения к БД или выполнения запроса.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return False

    try:
        with conn.cursor() as cur:
            # Выполнение SQL-запроса для обновления названия категории по ID
            cur.execute("""
                UPDATE categories
                SET name = %s
                WHERE id = %s;
            """, (new_name, category_id))
            conn.commit()  # Фиксация изменений

            return True
    except psycopg2.Error as e:
        print(f"Ошибка БД при переименовании категории: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"Неизвестная ошибка при переименовании категории: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_category_func(category_id: int):
    """
    "Мягко" удаляет категорию, помечая её как удалённую и записывая время удаления.
    Физическое удаление (и связанных трат) происходит позже с помощью фонового задания.

    Args:
        category_id (int): Уникальный идентификатор категории для удаления.

    Returns:
        bool: True, если категория успешно помечена как удалённая, False в противном случае.
              Возвращает False также в случае ошибки подключения к БД или выполнения запроса.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return False

    try:
        with conn.cursor() as cur:
            # Обновление записи категории: установка флага is_deleted в TRUE
            # и заполнение поля deleted_at текущим временем.
            cur.execute("""
                UPDATE categories
                SET is_deleted = TRUE, deleted_at = NOW()
                WHERE id = %s
            """, (category_id,))
            conn.commit()  # Фиксация изменений
            return True

    except psycopg2.Error as e:
        print(f"Ошибка БД при мягком удалении категории: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"Неизвестная ошибка при мягком удалении категории: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
