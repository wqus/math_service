from aiogram.fsm.state import State, StatesGroup


# Класс состояний для поддержки
class SupportStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_answer = State()
