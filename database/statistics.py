import psycopg2

from database.connection import connect_db


def statistics_for_week_or_month(user_id: int, start_date: str, end_date: str):
    """
    Вычисляет общую сумму расходов пользователя за указанный период (неделю или месяц).

    Args:
        user_id (int): ID пользователя.
        start_date (str): Начальная дата периода в формате 'YYYY-MM-DD'.
        end_date (str): Конечная дата периода в формате 'YYYY-MM-DD'.

    Returns:
        float: Общая сумма расходов за период. Возвращает 0.0 в случае отсутствия расходов,
               ошибки подключения к БД или выполнения запроса.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return 0.0

    try:
        with conn.cursor() as cur:
            # SQL-запрос для суммирования расходов пользователя за период
            cur.execute("""
                SELECT SUM(amount) FROM expenses
                WHERE user_id = %s AND date >= %s AND date < %s
            """, (user_id, start_date, end_date))
            res = cur.fetchone()
            if res and res[0] is not None:
                return float(res[0])
            return 0.0

    except psycopg2.Error as e:
        print(f"Ошибка БД при подсчёте общей статистики: {e}")
        return 0.0
    except Exception as e:
        print(f"Неизвестная ошибка при подсчёте общей статистики: {e}")
        return 0.0
    finally:
        if conn:
            conn.close()


def statistics_by_category(user_id: int, start_date: str, end_date: str):
    """
    Получает сумму расходов по каждой категории для заданного пользователя
    за указанный период. Включает информацию о том, удалена ли категория.

    Args:
        user_id (int): ID пользователя.
        start_date (str): Начальная дата периода в формате 'YYYY-MM-DD'.
        end_date (str): Конечная дата периода в формате 'YYYY-MM-DD'.

    Returns:
        list[dict]: Список словарей, где каждый словарь представляет категорию
                    с её именем, общей суммой расходов и статусом удаления.
                    Пример: [{'name': 'Еда', 'amount': 150.0, 'is_deleted': False}].
                    Возвращает пустой список в случае ошибки или отсутствия данных.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return []

    try:
        with conn.cursor() as cur:
            # SQL-запрос для получения сумм расходов по категориям.
            # Используется JOIN для связывания расходов с информацией о категориях (имя, статус удаления).
            # Группировка по имени и статусу is_deleted позволяет получить суммы для каждой уникальной
            # комбинации категории и ее статуса.
            cur.execute("""
                SELECT c.name, SUM(e.amount), c.is_deleted
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE e.user_id = %s AND e.date >= %s AND e.date < %s
                GROUP BY c.name, c.is_deleted
                ORDER BY SUM(e.amount) DESC; -- Сортировка по убыванию суммы
            """, (user_id, start_date, end_date))
            res = cur.fetchall()

            category_and_amount = []
            for row in res:
                category_name, total_amount, is_deleted = row
                category_and_amount.append({
                    'name': category_name,
                    'amount': total_amount if total_amount is not None else 0.0,
                    'is_deleted': is_deleted
                })

        return category_and_amount

    except psycopg2.Error as e:
        print(f"Ошибка БД при подсчёте статистики по категориям: {e}")
        return []
    except Exception as e:
        print(f"Неизвестная ошибка при подсчёте статистики по категориям: {e}")
        return []
    finally:
        if conn:
            conn.close()


def full_statistics(user_id: int, start_date: str, end_date: str) -> dict:
    """
    Собирает полную статистику расходов пользователя за указанный период,
    включая общую сумму и разбиение по категориям.

    Args:
        user_id (int): ID пользователя.
        start_date (str): Начальная дата периода в формате 'YYYY-MM-DD'.
        end_date (str): Конечная дата периода в формате 'YYYY-MM-DD'.

    Returns:
        dict: Словарь с полной статистикой:
              - 'total_expenses' (float): Общая сумма расходов.
              - 'expenses_by_category' (list[dict]): Список расходов по категориям.
    """
    total_expenses = statistics_for_week_or_month(user_id, start_date, end_date)
    expenses_by_category = statistics_by_category(user_id, start_date, end_date)

    return {
        'total_expenses': total_expenses,
        'expenses_by_category': expenses_by_category
    }
