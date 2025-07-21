from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.user_data import (find_user_id_by_telegram_id,
                                get_user_categories_names_and_ids)


def category_kb(message: types.Message, callback_prefix: str) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру с кнопками для выбора категорий пользователя.
    Предлагает создать новую категорию, если у пользователя их нет.
    Отображает только активные (неудаленные) категории.

    Args:
        message (types.Message): Объект сообщения, от которого исходит запрос (используется для получения ID пользователя).
        callback_prefix (str): Префикс, который будет добавлен к callback_data каждой кнопки категории.
                               Это позволяет обработчикам различать, для какой цели была выбрана категория.

    Returns:
        InlineKeyboardMarkup: Объект инлайн-клавиатуры.
    """
    markup = InlineKeyboardMarkup()

    # Находим внутренний ID пользователя в базе данных по его Telegram ID
    user_id_in_db = find_user_id_by_telegram_id(telegram_id=message.from_user.id)
    if user_id_in_db is None:
        # Если пользователь не найден в БД, возвращаем пустую клавиатуру
        return markup

    # Получаем список АКТИВНЫХ категорий пользователя из базы данных
    categories = get_user_categories_names_and_ids(user_id_in_db)

    if not categories:
        # Если у пользователя нет активных категорий, предлагаем создать новую
        markup.add(InlineKeyboardButton(
            text='Добавьте категории для выбора',
            callback_data='create_new_category_prompt'
        ))
        return markup

    buttons_in_row = [] # Временный список для хранения кнопок в текущей строке
    # Определяем количество колонок: 2, если категорий 4 или меньше, иначе 3.
    # Это помогает равномерно распределить кнопки.
    num_cols = 2 if len(categories) <= 4 else 3

    for category in categories: # Теперь итерируемся по всем полученным категориям
        # Создаем кнопку для каждой активной категории
        button = InlineKeyboardButton(
            text=category['name'],
            callback_data=f"{callback_prefix}{category['id']}" # Формируем callback_data с префиксом и ID категории
        )
        buttons_in_row.append(button)

        # Если количество кнопок в текущей строке достигло num_cols, добавляем их в разметку
        if len(buttons_in_row) == num_cols:
            markup.row(*buttons_in_row) # Распаковываем список кнопок в аргументы row
            buttons_in_row = [] # Сбрасываем список для следующей строки

    # Добавляем оставшиеся кнопки, если они есть (последняя неполная строка)
    if buttons_in_row:
        markup.row(*buttons_in_row)

    return markup
