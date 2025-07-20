from telebot import types, TeleBot

from database.category import get_category_name_by_id
from database.category import delete_category_func
from inline_keyboard.categories import category_kb
from inline_keyboard.delete_confirmation import delete_category_confirmation
from messages import (
    choose_category,
    choose_category_error,
    delete_category_confirmation_msg,
    error_category_not_found,
    delete_category_success,
    delete_msg_error,
    delete_category_cancel_msg,
)
from states import UserState


def handle_delete_category_button(message: types.Message, bot: TeleBot):
    """
    Обрабатывает нажатие кнопки "🗑️ Удалить категорию".
    Отправляет пользователю сообщение с инлайн-клавиатурой для выбора категории на удаление.

    Args:
        message (types.Message): Объект сообщения от пользователя.
        bot (TeleBot): Экземпляр бота.
    """
    callback_prefix = 'delete_category:' # Префикс для callback_data кнопок категорий
    # Генерируем инлайн-клавиатуру с категориями пользователя
    categories_markup = category_kb(message, callback_prefix)
    bot.send_message(
        chat_id=message.chat.id,
        text=choose_category,
        reply_markup=categories_markup
    )


def handler_category_selection_for_delete(query: types.CallbackQuery, bot: TeleBot):
    """
    Обрабатывает выбор категории пользователем для удаления (после нажатия кнопки).
    Запрашивает подтверждение удаления у пользователя, отображая имя категории.

    Args:
        query (types.CallbackQuery): Объект callback-запроса от нажатой кнопки.
        bot (TeleBot): Экземпляр бота.
    """
    bot.answer_callback_query(query.id) # Отвечаем на callback_query, чтобы убрать индикатор загрузки на кнопке

    try:
        # Извлекаем ID категории из callback_data (формат 'префикс:ID')
        category_id = int(query.data.split(':')[1])
    except (ValueError, IndexError):
        print(f"ERROR: Неверный формат callback data в handler_category_selection_for_delete: {query.data}")
        bot.send_message(query.message.chat.id, choose_category_error)
        bot.set_state(query.message.chat.id, UserState.DEFAULT)
        return

    # Получаем название категории по её ID из базы данных
    category_name = get_category_name_by_id(category_id)
    if not category_name:
        bot.send_message(query.message.chat.id, error_category_not_found)
        bot.set_state(query.message.chat.id, UserState.DEFAULT)
        return

    # Редактируем сообщение, чтобы запросить подтверждение
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=delete_category_confirmation_msg.format(category_name=category_name), # Форматируем сообщение с именем категории
        reply_markup=delete_category_confirmation(category_id),
        parse_mode='Markdown' # Указываем режим парсинга, если в сообщении есть Markdown
    )


def delete_category(query: types.CallbackQuery, bot: TeleBot):
    """
    Обрабатывает подтверждение или отмену удаления категории.
    В зависимости от выбора пользователя, выполняет мягкое удаление категории или отменяет операцию.

    Args:
        query (types.CallbackQuery): Объект callback-запроса (от кнопок подтверждения/отмены).
        bot (TeleBot): Экземпляр бота.
    """
    bot.answer_callback_query(query.id) # Отвечаем на callback_query

    data = query.data
    if not data:
        bot.send_message(query.message.chat.id, "Ошибка: callback data не получена.")
        bot.set_state(query.message.chat.id, UserState.DEFAULT)
        return

    try:
        # Извлекаем ID категории из callback_data
        category_id = int(data.split(':')[1])
    except (ValueError, IndexError):
        # Обработка некорректного формата ID
        bot.send_message(query.message.chat.id, "Ошибка: Неверный формат ID категории в запросе.")
        bot.set_state(query.message.chat.id, UserState.DEFAULT)
        return

    # Пытаемся удалить исходное сообщение с вопросом подтверждения, чтобы не загромождать чат
    try:
        bot.delete_message(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id
        )
    except Exception as e:
        print(f"Ошибка удаления сообщения в delete_category: {e}")
        # Продолжаем выполнение, даже если сообщение не удалось удалить

    if data.startswith('confirm_delete:'):
        # Если пользователь подтвердил удаление
        if delete_category_func(category_id):
            bot.send_message(
                chat_id=query.message.chat.id,
                text=delete_category_success
            )
        else:
            bot.send_message(
                chat_id=query.message.chat.id,
                text=delete_msg_error
            )
        # Сбрасываем состояние после выполнения операции (удаления или ошибки)
        bot.set_state(query.message.chat.id, UserState.DEFAULT)

    elif data.startswith('cancel_delete:'):
        # Если пользователь отменил удаление
        bot.send_message(
            chat_id=query.message.chat.id,
            text=delete_category_cancel_msg
        )
        # Сбрасываем состояние после отмены
        bot.set_state(query.message.chat.id, UserState.DEFAULT)
