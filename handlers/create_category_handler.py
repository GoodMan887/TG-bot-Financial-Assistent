from telebot import TeleBot, types

from database.category import create_category, is_valid_category_name
from database.user_data import find_user_id_by_telegram_id
from messages import (create_category_error, create_category_message,
                      create_category_success, error_user_not_found,
                      valid_category_name)
from states import UserState


def handle_create_category_button(message: types.Message, bot: TeleBot):
    """
    Обрабатывает нажатие кнопки "💲 Создать категорию".
    Переводит пользователя в состояние ожидания названия категории и запрашивает его.

    Args:
        message (types.Message): Объект сообщения от пользователя.
        bot (TeleBot): Экземпляр бота.
    """
    # Устанавливаем состояние пользователя на WAITING_FOR_CATEGORY_NAME,
    # чтобы следующий текстовый ввод был интерпретирован как название категории.
    bot.set_state(message.chat.id, UserState.WAITING_FOR_CATEGORY_NAME)
    bot.send_message(
        chat_id=message.chat.id,
        text=create_category_message
    )


def save_new_category(message: types.Message, bot: TeleBot):
    """
    Обрабатывает ввод пользователя в состоянии WAITING_FOR_CATEGORY_NAME.
    Пытается создать новую категорию в базе данных.

    Args:
        message (types.Message): Объект сообщения с названием категории от пользователя.
        bot (TeleBot): Экземпляр бота.
    """
    # Ищем внутренний ID пользователя в БД по его Telegram ID
    user_id = find_user_id_by_telegram_id(telegram_id=message.from_user.id)

    if user_id is None:
        bot.send_message(
            chat_id=message.chat.id,
            text=error_user_not_found
        )
        bot.set_state(message.chat.id, UserState.DEFAULT)
        return

    category_name = message.text

    if not is_valid_category_name(category_name):
        bot.send_message(
            chat_id=message.chat.id,
            text=valid_category_name
        )
        bot.set_state(message.chat.id, UserState.DEFAULT)
        return

    # Пытаемся создать категорию в базе данных
    if create_category(user_id, category_name):
        # В случае успеха отправляем сообщение об успешном создании
        bot.send_message(
            chat_id=message.chat.id,
            text=create_category_success
        )
    else:
        # В случае ошибки при создании категории в БД, отправляем сообщение об ошибке
        bot.send_message(
            chat_id=message.chat.id,
            text=create_category_error
        )

    # В любом случае, после обработки сбрасываем состояние пользователя на DEFAULT
    bot.set_state(message.chat.id, UserState.DEFAULT)
