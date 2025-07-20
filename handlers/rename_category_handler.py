from telebot import types, TeleBot

from database.category import rename_category_in_db
from inline_keyboard.categories import category_kb
from messages import (
    rename_category_msg,
    rename_category_success,
    rename_category_error,
    delete_msg_error,
    choose_category_error,
    choose_category,
)
from states import UserState


def handle_rename_category_button(message: types.Message, bot: TeleBot):
    """
    Обрабатывает нажатие кнопки "✏️ Переименовать категорию".
    Отправляет пользователю сообщение с инлайн-клавиатурой для выбора категории, которую нужно переименовать.

    Args:
        message (types.Message): Объект сообщения от пользователя, содержащий текст кнопки.
        bot (TeleBot): Экземпляр бота.
    """
    callback_prefix = 'rename_category:' # Префикс для callback_data кнопок категорий
    # Генерируем инлайн-клавиатуру с категориями пользователя
    categories_markup = category_kb(message, callback_prefix)
    bot.send_message(
        chat_id=message.chat.id,
        text=choose_category,
        reply_markup=categories_markup
    )


def handle_category_selection_for_rename(query: types.CallbackQuery, bot: TeleBot):
    """
    Обрабатывает выбор категории пользователем для переименования (после нажатия инлайн-кнопки).
    Сохраняет выбранный ID категории в состояние пользователя и запрашивает новое название.

    Args:
        query (types.CallbackQuery): Объект callback-запроса от нажатой кнопки категории.
        bot (TeleBot): Экземпляр бота.
    """
    bot.answer_callback_query(query.id) # Отвечаем на callback_query, чтобы убрать индикатор загрузки на кнопке

    try:
        # Извлекаем ID категории из callback_data (формат 'префикс:ID')
        category_id = int(query.data.split(':')[1])
    except (ValueError, IndexError):
        print(f"ERROR: Неверный формат callback data в handle_category_selection_for_rename: {query.data}")
        bot.send_message(query.message.chat.id, choose_category_error) # Сообщение об ошибке
        return

    # Устанавливаем состояние пользователя в ожидание нового названия категории
    bot.set_state(query.message.chat.id, UserState.WAITING_FOR_NEW_CATEGORY_NAME)

    # Редактируем сообщение, чтобы запросить новое название категории
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=rename_category_msg
    )

    # Сохраняем ID выбранной категории в данные состояния пользователя
    bot.current_states.set_data(
        chat_id=query.message.chat.id,
        user_id=query.from_user.id,
        key='selected_rename_category_id',
        value=category_id
    )

    # Сохраняем ID сообщения, которое просит ввести новое название.
    # Это нужно для последующего удаления этого сообщения после ввода названия.
    bot.current_states.set_data(
        chat_id=query.message.chat.id,
        user_id=query.from_user.id,
        key='prompt_message_id',
        value=query.message.message_id
    )


def rename_category(message: types.Message, bot: TeleBot):
    """
    Обрабатывает ввод пользователем нового названия категории в состоянии WAITING_FOR_NEW_CATEGORY_NAME.
    Пытается переименовать категорию в базе данных.

    Args:
        message (types.Message): Объект сообщения с новым названием категории от пользователя.
        bot (TeleBot): Экземпляр бота.
    """
    # Получаем сохраненные данные состояния пользователя
    user_data = bot.current_states.get_data(
        chat_id=message.chat.id,
        user_id=message.from_user.id
    )
    # Извлекаем ID категории, которую нужно переименовать
    category_id = user_data.get('selected_rename_category_id')
    # Извлекаем ID сообщения, которое запросило новое название (для последующего удаления)
    prompt_msg_id = user_data.get('prompt_message_id')

    # Если ID категории отсутствует в состоянии (некорректный флоу или ошибка), сообщаем
    if category_id is None:
        bot.send_message(message.chat.id, choose_category_error) # Сообщение об ошибке
        bot.set_state(message.chat.id, UserState.DEFAULT) # Сбрасываем состояние
        return

    # Пытаемся переименовать категорию в базе данных
    if rename_category_in_db(category_id, message.text):
        # В случае успеха
        bot.send_message(
            chat_id=message.chat.id,
            text=rename_category_success, # Сообщение об успешном переименовании
        )
        # Если ID сообщения-запроса был сохранен, пытаемся его удалить
        if prompt_msg_id:
            try:
                bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=prompt_msg_id
                )
            except Exception as e:
                # Логируем ошибку, если не удалось удалить сообщение
                print(f'{delete_msg_error}: {e}')
    else:
        # В случае ошибки при переименовании в БД
        bot.send_message(
            chat_id=message.chat.id,
            text=rename_category_error
        )

    # После выполнения операции сбрасываем состояние пользователя
    bot.set_state(message.chat.id, UserState.DEFAULT)
