from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import kb_for_statistics


def create_time_interval_markup(callback_prefix: str) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру с кнопками выбора временного промежутка для статистики.

    Args:
        callback_prefix (str): Префикс для callback_data каждой кнопки.
                               Это позволяет обработчикам различать, для какого типа статистики
                               был выбран интервал (например, 'time_interval_' для общей статистики,
                               'time_interval_for_basic_expenses_' для основных трат).

    Returns:
        InlineKeyboardMarkup: Объект инлайн-клавиатуры с кнопками временных интервалов.
    """
    markup = InlineKeyboardMarkup()
    for interval_key, button_text in kb_for_statistics.items(): # Итерируемся по элементам словаря
        button = InlineKeyboardButton(
            text=button_text,
            callback_data=f'{callback_prefix}{interval_key}'
        )
        markup.row(button) # Каждая кнопка в новой строке
    return markup
