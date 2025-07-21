import psycopg2

from database.connection import connect_db


def write_down_expense(user_id: int, category_id: int, amount: float):
    """
    Записывает новую транзакцию расхода в базу данных.

    Args:
        user_id (int): ID пользователя, совершившего расход.
        category_id (int): ID категории, к которой относится расход.
        amount (float): Сумма расхода.

    Returns:
        bool: True, если расход успешно записан, False в противном случае.
              Возвращает False также в случае ошибки подключения к БД или выполнения запроса.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return False

    try:
        with conn.cursor() as cur:
            # SQL-запрос для вставки новой записи о расходе
            # Предполагается, что поле date в таблице expenses имеет DEFAULT NOW()
            cur.execute("""
            INSERT INTO expenses (user_id, category_id, amount)
            VALUES (%s, %s, %s)
            """, (user_id, category_id, amount))
            conn.commit() # Фиксация изменений в базе данных
            return True
    except psycopg2.Error as e:
        print(f"Ошибка БД при записи расходов: {e}")
        if conn:
            conn.rollback() # Откат транзакции в случае ошибки
        return False
    except Exception as e:
        print(f"Неизвестная ошибка при записи расходов: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def get_top_categories_and_other_sum(user_id: int, start_date: str, end_date: str):
    """
    Получает топ-3 категории расходов пользователя за указанный период
    и суммирует остальные расходы в категорию 'Остальное'.

    Args:
        user_id (int): ID пользователя, для которого запрашиваются данные.
        start_date (str): Начальная дата периода в формате 'YYYY-MM-DD'.
        end_date (str): Конечная дата периода в формате 'YYYY-MM-DD'.

    Returns:
        dict: Словарь с двумя ключами:
              - 'top_categories' (list[dict]): Список словарей с именами и суммами
                для топ-3 категорий. Пример: [{'name': 'Еда', 'amount': 100.0}].
              - 'other_sum' (float): Сумма расходов по всем остальным категориям.
              Возвращает {'top_categories': [], 'other_sum': 0.0} в случае ошибки
              или отсутствия данных.
    """
    conn = connect_db()
    if conn is None:
        print("Ошибка: Не удалось подключиться к базе данных.")
        return {'top_categories': [], 'other_sum': 0.0}

    try:
        with conn.cursor() as cur:
            # SQL-запрос использует Common Table Expressions (CTE) для сложной выборки:
            # 1. UserCategorySums: Суммирует расходы по категориям для данного пользователя в заданном диапазоне дат,
            #    исключая удаленные категории.
            # 2. UserExpensesWithNames: Присоединяет названия категорий к их суммам.
            # 3. RankedExpenses: Ранжирует категории по убыванию суммы расходов.
            # Финальная выборка UNION ALL объединяет топ-3 категории с суммой остальных.
            cur.execute("""
                WITH UserCategorySums AS (
                    SELECT
                        e.category_id,
                        SUM(e.amount) AS total_amount
                    FROM
                        expenses AS e
                    JOIN
                        categories AS c ON e.category_id = c.id
                    WHERE
                        e.user_id = %s
                        AND e.date BETWEEN %s AND %s
                        AND c.is_deleted = FALSE -- Учитываем только активные (неудаленные) категории
                    GROUP BY
                        e.category_id
                ),
                UserExpensesWithNames AS (
                    SELECT
                        c.name AS category_name,
                        ucs.total_amount
                    FROM
                        UserCategorySums AS ucs
                    JOIN
                        categories AS c ON ucs.category_id = c.id
                ),
                RankedExpenses AS (
                    SELECT
                        category_name,
                        total_amount,
                        ROW_NUMBER() OVER (ORDER BY total_amount DESC) as rn -- Ранжируем категории по сумме
                    FROM
                        UserExpensesWithNames
                )
                SELECT
                    category_name,
                    total_amount
                FROM
                    RankedExpenses
                WHERE
                    rn <= 3 -- Выбираем топ-3 категории

                UNION ALL -- Объединяем с результатами для "Остального"

                SELECT
                    'Остальное' AS category_name,
                    SUM(total_amount) AS total_amount
                FROM
                    RankedExpenses
                WHERE
                    rn > 3; -- Суммируем все остальные категории
            """, (user_id, start_date, end_date))

            results = cur.fetchall()

            top_categories = []
            other_sum = 0.0

            # Разбор результатов запроса
            for category_name, amount in results:
                if category_name == 'Остальное':
                    other_sum = float(amount) if amount is not None else 0.0
                else:
                    top_categories.append({'name': category_name, 'amount': float(amount or 0.0)})

            # Сортировка топ-категорий по убыванию суммы (на случай, если UNION ALL нарушил порядок)
            top_categories.sort(key=lambda x: x['amount'], reverse=True)

            return {'top_categories': top_categories, 'other_sum': other_sum}

    except psycopg2.Error as e:
        print(f"Ошибка БД при получении топ категорий: {e}")
        return {'top_categories': [], 'other_sum': 0.0}
    except Exception as e:
        print(f"Неизвестная ошибка при получении топ категорий: {e}")
        return {'top_categories': [], 'other_sum': 0.0}
    finally:
        if conn:
            conn.close()
