from telebot import TeleBot

from handlers.create_category_handler import (handle_create_category_button,
                                              save_new_category)
from handlers.delete_category_handler import (
    delete_category, handle_delete_category_button,
    handler_category_selection_for_delete)
from handlers.expenses_handler import (handle_category_selection_for_expense,
                                       handle_expense_button, write_expenses)
from handlers.rename_category_handler import (
    handle_category_selection_for_rename, handle_rename_category_button,
    rename_category)
from handlers.start import echo_msg, handle_command_start
from handlers.statistics_handler import (handle_basic_expenses_button,
                                         handle_statistics_button,
                                         handle_statistics_interval_callback)

# --- Функции регистрации обработчиков сообщений ---

def register_start_command_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для команды '/start'.
    """
    bot.register_message_handler(
        callback=handle_command_start,
        commands=['start'],
        pass_bot=True # Передача экземпляра бота в обработчик
    )


def register_create_category_message_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для кнопки "💲 Создать категорию".
    """
    bot.register_message_handler(
        callback=handle_create_category_button,
        func=lambda message: message.text == '💲 Создать категорию', # Фильтр по тексту кнопки
        pass_bot=True
    )


def register_save_category_name_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для сохранения нового названия категории,
    когда пользователь находится в соответствующем состоянии.
    """
    bot.register_message_handler(
        callback=save_new_category,
        # Проверяем, что пользователь находится в состоянии ожидания названия категории,
        # используя строковое представление состояния.
        func=lambda message: bot.get_state(message.chat.id) == 'UserState:WAITING_FOR_CATEGORY_NAME',
        content_types=['text'], # Обрабатываем только текстовые сообщения
        pass_bot=True
    )


def register_rename_category_message_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для кнопки "✏️ Переименовать категорию".
    """
    bot.register_message_handler(
        callback=handle_rename_category_button,
        func=lambda message: message.text == '✏️ Переименовать категорию',
        pass_bot=True
    )


def register_save_new_category_name_message_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для сохранения нового названия переименованной категории,
    когда пользователь находится в соответствующем состоянии.
    """
    bot.register_message_handler(
        callback=rename_category,
        func=lambda message: bot.get_state(message.chat.id) == 'UserState:WAITING_FOR_NEW_CATEGORY_NAME',
        content_types=['text'],
        pass_bot=True
    )


def register_delete_category_message_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для кнопки "🗑️ Удалить категорию".
    """
    bot.register_message_handler(
        callback=handle_delete_category_button,
        func=lambda message: message.text == '🗑️ Удалить категорию',
        pass_bot=True
    )


def register_expense_message_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для кнопки "✍️ Записать расходы".
    """
    bot.register_message_handler(
        callback=handle_expense_button,
        func=lambda message: message.text == '✍️ Записать расходы',
        pass_bot=True
    )


def register_expense_amount_message_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для сохранения суммы расхода,
    когда пользователь находится в соответствующем состоянии.
    """
    bot.register_message_handler(
        callback=write_expenses,
        func=lambda message: bot.get_state(message.chat.id) == 'UserState:WAITING_FOR_EXPENSE_AMOUNT',
        content_types=['text'],
        pass_bot=True
    )


def register_statistics_message_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для кнопки "📊 Статистика".
    """
    bot.register_message_handler(
        callback=handle_statistics_button,
        func=lambda message: message.text == '📊 Статистика',
        pass_bot=True
    )


def register_basic_expenses_message_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для кнопки "📉 Основные траты".
    """
    bot.register_message_handler(
        callback=handle_basic_expenses_button,
        func=lambda message: message.text == '📉 Основные траты',
        pass_bot=True
    )


def register_echo_message_handler(bot: TeleBot) -> None:
    """
    Регистрирует "эхо" обработчик для всех остальных текстовых сообщений.
    Должен быть зарегистрирован последним, чтобы не перехватывать другие команды.
    """
    bot.register_message_handler(
        callback=echo_msg,
        func=lambda message: True, # Обрабатывает любое сообщение
        pass_bot=True
    )


# --- Функции регистрации обработчиков CallbackQuery (инлайн-кнопки) ---

def register_rename_category_callback_query_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для выбора категории при переименовании.
    """
    bot.register_callback_query_handler(
        callback=handle_category_selection_for_rename,
        func=lambda query: query.data.startswith('rename_category:'), # Фильтр по префиксу callback_data
        pass_bot=True
    )


def register_delete_category_selection_callback_query_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для выбора категории при удалении.
    """
    bot.register_callback_query_handler(
        callback=handler_category_selection_for_delete,
        func=lambda query: query.data.startswith('delete_category:'),
        pass_bot=True
    )


def register_delete_category_confirmation_callback_query_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для подтверждения/отмены удаления категории.
    """
    bot.register_callback_query_handler(
        callback=delete_category,
        func=lambda query: query.data.startswith('confirm_delete:') or \
                           query.data.startswith('cancel_delete:'), # Фильтр для кнопок подтверждения/отмены
        pass_bot=True
    )


def register_expense_category_callback_query_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для выбора категории при записи расхода.
    """
    bot.register_callback_query_handler(
        callback=handle_category_selection_for_expense,
        func=lambda query: query.data.startswith('select_expense_category:'),
        pass_bot=True
    )


def register_statistics_interval_callback_query_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик для выбора временного интервала для статистики (как общей, так и основных трат).
    """
    # Этот обработчик универсален для обоих типов статистики, так как handle_statistics_interval_callback
    # сама различает их по префиксу 'time_interval_' и 'time_interval_for_basic_expenses_'
    # Поэтому достаточно одного обработчика, который ловит оба префикса.
    bot.register_callback_query_handler(
        callback=handle_statistics_interval_callback,
        func=lambda query: query.data.startswith('time_interval_'),
        pass_bot=True
    )


# --- Основная функция для регистрации всех хендлеров ---

def register_all_handlers(bot: TeleBot) -> None:
    """
    Регистрирует все обработчики сообщений и callback-запросов бота.
    """
    register_start_command_handler(bot)

    register_create_category_message_handler(bot)
    register_save_category_name_handler(bot) # Это обработчик состояния

    register_rename_category_message_handler(bot)
    register_save_new_category_name_message_handler(bot) # Это обработчик состояния

    register_delete_category_message_handler(bot)

    register_expense_message_handler(bot)
    register_expense_amount_message_handler(bot) # Это обработчик состояния

    register_statistics_message_handler(bot)
    register_basic_expenses_message_handler(bot)

    # Регистрируем обработчики CallbackQuery (InlineKeyboardMarkup кнопки)
    register_rename_category_callback_query_handler(bot)
    register_delete_category_selection_callback_query_handler(bot)
    register_delete_category_confirmation_callback_query_handler(bot)
    register_expense_category_callback_query_handler(bot)
    register_statistics_interval_callback_query_handler(bot)

    register_echo_message_handler(bot)
