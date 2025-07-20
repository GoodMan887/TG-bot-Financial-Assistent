from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import kb_for_delete_confirmation


def delete_category_confirmation(category_id: int) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру с кнопками для подтверждения или отмены удаления категории.

    Args:
        category_id (int): ID категории, которую предполагается удалить.
                           Этот ID будет включен в callback_data кнопок подтверждения/отмены.

    Returns:
        InlineKeyboardMarkup: Объект инлайн-клавиатуры с кнопками "Да" и "Нет".
    """
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text=kb_for_delete_confirmation['del'], # Текст кнопки из конфига
            callback_data=f"confirm_delete:{category_id}" # Callback_data для подтверждения
        ),
        InlineKeyboardButton(
            text=kb_for_delete_confirmation['cancel'], # Текст кнопки из конфига
            callback_data=f"cancel_delete:{category_id}" # Callback_data для отмены
        )
    )
    return markup
