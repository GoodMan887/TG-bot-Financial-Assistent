import telebot
import threading
import time
from telebot.storage import StateMemoryStorage

from config import BOT_TOKEN
from handlers.register import register_all_handlers
from database.clean_old_categories import delete_old_deleted_categories

# Инициализируем хранилище состояний FSM
storage = StateMemoryStorage()

# Создаём экземпляр бота с токеном и FSM
bot = telebot.TeleBot(BOT_TOKEN, state_storage=storage)


def register_handlers():
    """Регистрирует все обработчики команд, сообщений и состояний."""
    register_all_handlers(bot)


register_handlers()


def start_cleanup_scheduler():
    """
    Запускает фоновый поток, который ежедневно удаляет
    старые удалённые категории из базы данных.
    """
    def job():
        while True:
            try:
                delete_old_deleted_categories()
            except Exception as e:
                print(f'[!] Ошибка при очистке категорий: {e}')
            time.sleep(24 * 60 * 60)  # запуск раз в сутки

    t = threading.Thread(target=job)
    t.daemon = True  # не мешает завершению основной программы
    t.start()


if __name__ == '__main__':
    start_cleanup_scheduler()
    bot.infinity_polling(skip_pending=True)
