from telebot import TeleBot, types

import messages
from config import key_board_buttons
from database.user_data import add_or_update_user
from states import UserState


def handle_command_start(message: types.Message, bot: TeleBot):
    """
    Обрабатывает команду '/start'.
    Регистрирует нового пользователя или обновляет данные существующего в базе данных.
    Устанавливает начальное состояние пользователя и отображает основное меню с клавиатурой.

    Args:
        message (types.Message): Объект сообщения от пользователя.
        bot (TeleBot): Экземпляр бота.
    """
    # Извлекаем информацию о пользователе из объекта сообщения
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    # Добавляем или обновляем информацию о пользователе в базе данных
    add_or_update_user(user_id, username, first_name, last_name)

    # Устанавливаем состояние пользователя по умолчанию (DEFAULT)
    bot.set_state(message.chat.id, UserState.DEFAULT)

    # Создаем объект ReplyKeyboardMarkup для отображения кнопок меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Добавляем кнопки в разметку
    markup.add(key_board_buttons['create_category'], key_board_buttons['rename_category'])
    markup.add(key_board_buttons['delete_category'], key_board_buttons['expenses'])
    markup.add(key_board_buttons['basic_expenses'], key_board_buttons['statistics'])

    # Отправляем приветственное сообщение с основной клавиатурой
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.start_message,
        reply_markup=markup
    )


def echo_msg(message: types.Message, bot: TeleBot):
    """
    Простой обработчик для "эхо-ответа" на любое текстовое сообщение,
    которое не было обработано другими хендлерами.
    Отправляет обратно тот же текст, что и получил.

    Args:
        message (types.Message): Объект сообщения от пользователя.
        bot (TeleBot): Экземпляр бота.
    """
    bot.send_message(
        chat_id=message.chat.id,
        text=message.text
    )
