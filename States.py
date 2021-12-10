from aiogram.dispatcher.filters.state import StatesGroup, State


class LearnLogInState(StatesGroup):
    ReadUserName = State()
    ReadPassword = State()


class SettingsState(StatesGroup):
    ReadSettingsAction = State()


class ChangeSubGroupState(StatesGroup):
    ReadSubGroup = State()


class ChangeMinutesBeforeLessonsNotificationState(StatesGroup):
    ReadMinutesBeforeLessonsNotification = State()

class ChangeMinutesBeforeLessonNotificationState(StatesGroup):
    ReadMinutesBeforeLessonNotification = State()


class SelectScheduleTypeState(StatesGroup):
    ReadScheduleType = State()
