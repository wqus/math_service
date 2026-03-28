from aiogram.fsm.state import State, StatesGroup


# класс состояний для графика
class PlotStates(StatesGroup):
    waiting_for_function = State()
