from aiogram.fsm.state import State, StatesGroup

class PlotStates(StatesGroup):#класс состояний для графика
    waiting_for_function = State()
