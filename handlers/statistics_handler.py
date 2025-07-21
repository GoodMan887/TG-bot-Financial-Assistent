import os

from telebot import TeleBot, types

from charts.statistics_charts import generate_expense_charts
from charts.top_categories_charts import generate_top_categories_pie
from config import days_for_statistics
from database.expenses import get_top_categories_and_other_sum
from database.statistics import full_statistics
from database.user_data import find_user_id_by_telegram_id
from inline_keyboard.statistics import create_time_interval_markup
from messages import (error_user_not_found, select_statistics_interval,
                      statistics_error)
from time_interval import get_time_interval


def handle_statistics_button(message: types.Message, bot: TeleBot):
    """
    Обрабатывает нажатие кнопки "📊 Статистика".
    Отправляет пользователю сообщение с инлайн-клавиатурой для выбора временного интервала
    для общей статистики и статистики по категориям.

    Args:
        message (types.Message): Объект сообщения от пользователя, содержащий текст кнопки.
        bot (TeleBot): Экземпляр бота.
    """
    # Создаем инлайн-клавиатуру с вариантами временных интервалов
    # Префикс 'time_interval_' будет использоваться для идентификации callback_data
    time_interval_markup = create_time_interval_markup('time_interval_')
    bot.send_message(
        chat_id=message.chat.id,
        text=select_statistics_interval,
        reply_markup=time_interval_markup
    )


def handle_basic_expenses_button(message: types.Message, bot: TeleBot):
    """
    Обрабатывает нажатие кнопки "📉 Основные траты".
    Отправляет пользователю сообщение с инлайн-клавиатурой для выбора временного интервала
    для статистики по основным категориям (круговой диаграммы).

    Args:
        message (types.Message): Объект сообщения от пользователя, содержащий текст кнопки.
        bot (TeleBot): Экземпляр бота.
    """
    # Создаем инлайн-клавиатуру с вариантами временных интервалов
    # Префикс 'time_interval_for_basic_expenses_' будет использоваться для идентификации callback_data
    time_interval_markup = create_time_interval_markup('time_interval_for_basic_expenses_')
    bot.send_message(
        chat_id=message.chat.id,
        text=select_statistics_interval,
        reply_markup=time_interval_markup
    )


def handle_statistics_interval_callback(query: types.CallbackQuery, bot: TeleBot):
    """
    Универсальный обработчик выбора временного интервала для статистики.
    Определяет, какой тип статистики запрашивается (общая или основные траты),
    получает данные, генерирует и отправляет соответствующие графики пользователю.

    Args:
        query (types.CallbackQuery): Объект callback-запроса от нажатой кнопки временного интервала.
        bot (TeleBot): Экземпляр бота.
    """
    bot.answer_callback_query(query.id) # Отвечаем на callback_query, чтобы убрать индикатор загрузки

    data_str = query.data

    # Определяем, какой тип статистики был запрошен, исходя из префикса callback_data
    if data_str.startswith('time_interval_for_basic_expenses_'):
        interval = data_str.replace('time_interval_for_basic_expenses_', '')
        is_basic = True # Это запрос на основные траты (круговая диаграмма)
    elif data_str.startswith('time_interval_'):
        interval = data_str.replace('time_interval_', '')
        is_basic = False # Это запрос на общую статистику (столбчатые диаграммы)
    else:
        # Если префикс не распознан, выходим из функции
        print(f"Неизвестный callback_data в handle_statistics_interval_callback: {data_str}")
        return

    # Получаем начальную и конечную даты на основе выбранного интервала
    dates = get_time_interval(days_for_statistics[interval])
    start_date, end_date = dates['start_date'], dates['end_date']

    # Находим внутренний ID пользователя в БД
    db_user_id = find_user_id_by_telegram_id(telegram_id=query.from_user.id)
    if db_user_id is None:
        bot.send_message(chat_id=query.message.chat.id, text=error_user_not_found)
        return

    # Удаляем сообщение с выбором интервала, чтобы не загромождать чат
    try:
        bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    except Exception as e:
        print(f"Ошибка удаления сообщения в handle_statistics_interval_callback: {e}")

    if is_basic:
        # 🔸 Обработка запроса на "Основные траты" (круговая диаграмма)
        data = get_top_categories_and_other_sum(db_user_id, start_date, end_date)
        if not data or (not data['top_categories'] and data['other_sum'] == 0.0): # Проверяем наличие данных
            bot.send_message(query.message.chat.id, statistics_error) # Если данных нет, сообщаем
            return

        # Генерируем круговую диаграмму и получаем путь к файлу
        chart_path = generate_top_categories_pie(data)
        if not chart_path or not os.path.exists(chart_path): # Проверяем, что файл создан
            bot.send_message(query.message.chat.id, statistics_error)
            return

        # Отправляем фотографию графика пользователю
        with open(chart_path, 'rb') as img:
            bot.send_photo(query.message.chat.id, img)
        os.remove(chart_path) # Удаляем временный файл графика

    else:
        # 🔹 Обработка запроса на "Статистику" (столбчатые диаграммы)
        data = full_statistics(db_user_id, start_date, end_date)
        # Проверяем наличие данных: общая сумма > 0 или есть категории с расходами
        if not data or (data['total_expenses'] == 0.0 and not data['expenses_by_category']):
            bot.send_message(query.message.chat.id, statistics_error)
            return

        # Генерируем столбчатые диаграммы и получаем список путей к файлам
        charts_paths = generate_expense_charts(data)

        if not charts_paths: # Если графики не были сгенерированы (например, нет данных)
            bot.send_message(query.message.chat.id, statistics_error)
            return

        if len(charts_paths) == 1:
            # Если только один график, отправляем его как фото
            with open(charts_paths[0], 'rb') as img:
                bot.send_photo(query.message.chat.id, img)
            os.remove(charts_paths[0]) # Удаляем временный файл
        else:
            # Если несколько графиков, отправляем их группой
            opened_images = [open(path, 'rb') for path in charts_paths]
            media = [types.InputMediaPhoto(img) for img in opened_images]
            bot.send_media_group(query.message.chat.id, media)
            # Закрываем все открытые файловые дескрипторы
            for img_file in opened_images:
                img_file.close()
            # Удаляем все временные файлы графиков
            for path in charts_paths:
                os.remove(path)
