from datetime import datetime, timedelta


def get_time_interval(days: int):
    """
    Вычисляет временной интервал (начальную и конечную даты) относительно текущего момента.

    Начальная дата: `days` дней назад, начиная с 00:00:00 текущего дня.
    Конечная дата: Текущий день, заканчивая 23:59:59.999999.

    Args:
        days (int): Количество дней, на которое нужно отсчитать назад от текущего дня.
                    Например, 0 для "сегодня", 7 для "за неделю", 30 для "за месяц".

    Returns:
        dict[str, datetime]: Словарь с ключами 'start_date' и 'end_date',
                             где значения - объекты datetime.
    """
    now = datetime.now()

    # Устанавливаем end_date на конец текущего дня (23:59:59.999999)
    end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Вычисляем start_date: текущая дата минус 'days' дней, сброшенная до начала дня (00:00:00.000000)
    start_date = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)

    return {'start_date': start_date, 'end_date': end_date}
