from aiogram.dispatcher.filters.state import StatesGroup, State


class LearnLogInState(StatesGroup):
    ReadUserName = State()
    ReadPassword = State()
