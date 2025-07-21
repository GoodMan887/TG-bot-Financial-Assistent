import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

key_board_buttons = {
    'create_category': '💲 Создать категорию',
    'expenses': '✍️ Записать расходы',
    'delete_category': '🗑️ Удалить категорию',
    'rename_category': '✏️ Переименовать категорию',
    'basic_expenses': '📉 Основные траты',
    'statistics': '📊 Статистика'
}

kb_for_statistics = {
    'week': 'За 1 неделю',
    'month': 'За 1 месяц'
}

kb_for_delete_confirmation = {
    'del': '✅ Удалить',
    'cancel': '❌ Отмена'
}

days_for_statistics = {
    'week': 7,
    'month': 30
}
