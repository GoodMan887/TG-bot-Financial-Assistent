from telebot.handler_backends import State, StatesGroup

class UserState(StatesGroup):
    """
    Класс, определяющий состояния пользователя в конечных автоматах бота.
    Каждое состояние соответствует определенному этапу взаимодействия с пользователем.
    """
    DEFAULT = State()
    WAITING_FOR_CATEGORY_NAME = State()
    WAITING_FOR_EXPENSE_CATEGORY = State()
    WAITING_FOR_EXPENSE_AMOUNT = State()
    WAITING_FOR_NEW_CATEGORY_NAME = State()
