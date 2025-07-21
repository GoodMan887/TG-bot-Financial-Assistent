from telebot import TeleBot, types

from database.expenses import write_down_expense
from database.user_data import find_user_id_by_telegram_id
from inline_keyboard.categories import category_kb
from messages import (enter_amount_error, error_user_not_found,
                      write_down_expense_choose_category_msg,
                      write_down_expense_error, write_down_expense_msg,
                      write_down_expense_success)
from states import UserState


def handle_expense_button(message: types.Message, bot: TeleBot):
    """
    Обрабатывает нажатие кнопки "✍️ Записать расходы".
    Запрашивает у пользователя выбор категории для расхода, отображая инлайн-клавиатуру.

    Args:
        message (types.Message): Объект сообщения от пользователя.
        bot (TeleBot): Экземпляр бота.
    """
    callback_prefix = 'select_expense_category:' # Префикс для callback_data кнопок категорий
    # Генерируем инлайн-клавиатуру с категориями пользователя
    categories_markup = category_kb(message, callback_prefix)
    bot.send_message(
        chat_id=message.chat.id,
        text=write_down_expense_choose_category_msg,
        reply_markup=categories_markup
    )


def handle_category_selection_for_expense(query: types.CallbackQuery, bot: TeleBot):
    """
    Обрабатывает выбор категории расхода пользователем (после нажатия кнопки).
    Сохраняет выбранный ID категории в состояние пользователя и запрашивает сумму расхода.

    Args:
        query (types.CallbackQuery): Объект callback-запроса от нажатой кнопки категории.
        bot (TeleBot): Экземпляр бота.
    """
    bot.answer_callback_query(query.id)

    try:
        # Извлекаем ID категории из callback_data (формат 'префикс:ID')
        category_id = int(query.data.split(':')[1])
    except (ValueError, IndexError):
        print(f"ОШИБКА: Неверный формат callback_data в handle_category_selection_for_expense: {query.data}")
        bot.send_message(query.message.chat.id, "Ошибка выбора категории")
        return

    # Устанавливаем состояние пользователя в ожидание ввода суммы расхода
    bot.set_state(query.message.chat.id, UserState.WAITING_FOR_EXPENSE_AMOUNT)
    # Сохраняем выбранный ID категории в данные состояния пользователя
    bot.current_states.set_data(
        chat_id=query.message.chat.id,
        user_id=query.from_user.id,
        key='selected_expense_category_id',
        value=category_id
    )

    # Редактируем сообщение, чтобы запросить ввод суммы
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=write_down_expense_msg
    )


def write_expenses(message: types.Message, bot: TeleBot):
    """
    Обрабатывает ввод суммы расхода пользователем в состоянии WAITING_FOR_EXPENSE_AMOUNT.
    Валидирует сумму, извлекает ID категории из состояния и записывает расход в БД.

    Args:
        message (types.Message): Объект сообщения с суммой расхода от пользователя.
        bot (TeleBot): Экземпляр бота.
    """
    # Ищем внутренний ID пользователя в БД по его Telegram ID
    db_user_id = find_user_id_by_telegram_id(telegram_id=message.from_user.id)
    if db_user_id is None:
        bot.send_message(
            chat_id=message.chat.id,
            text=error_user_not_found
        )
        bot.set_state(message.chat.id, UserState.DEFAULT)
        return

    # Получаем сохраненные данные состояния пользователя
    user_data = bot.current_states.get_data(
        chat_id=message.chat.id,
        user_id=message.from_user.id
    )
    # Извлекаем ID выбранной категории
    category_id = user_data.get('selected_expense_category_id')

    if category_id is None:
        bot.send_message(message.chat.id, "Ошибка: Категория не была выбрана. Начните заново.")
        bot.set_state(message.chat.id, UserState.DEFAULT)
        return

    try:
        # Очистка и преобразование введенной суммы:
        # Удаляем пробелы, заменяем запятые на точки для корректного преобразования в float
        cleaned_amount_str = message.text.replace(' ', '').replace(',', '.')
        amount = float(cleaned_amount_str)
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
    except ValueError:
        # Обработка ошибки, если введенная сумма некорректна
        bot.send_message(
            chat_id=message.chat.id,
            text=enter_amount_error
        )
        return # Не сбрасываем состояние, чтобы пользователь мог повторно ввести сумму

    # Пытаемся записать расход в базу данных
    if write_down_expense(db_user_id, category_id, amount):
        # В случае успеха
        bot.send_message(
            chat_id=message.chat.id,
            text=write_down_expense_success
        )
    else:
        # В случае ошибки при записи в БД
        bot.send_message(
            chat_id=message.chat.id,
            text=write_down_expense_error
        )

    # После успешной записи или фатальной ошибки, сбрасываем состояние пользователя
    bot.set_state(message.chat.id, UserState.DEFAULT)
