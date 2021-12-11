from aiogram import types

ScheduleForToday = 'На сьогодні'
ScheduleForTomorrow = 'На завтра'
ScheduleForTwoWeeks = 'На 2 тижні'
More = 'Більше'
mainKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [ScheduleForToday, ScheduleForTomorrow, ScheduleForTwoWeeks, More]
mainKeyboard.add(*buttons)

Profile = 'Профіль'
Marks = 'Оцінки'
Settings = '⚙️ Налаштування'
LogOut = '🚪 Вийти'
Back = '🔙 Назад'
moreKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [Profile, Marks, Settings, LogOut, Back]
moreKeyboard.add(*buttons)

SettingsChangeSubGroup = 'Змінити підгрупу'
SettingsChangeMinutesBeforeLessonNotification = '🛎️ Змінити час сповіщення перед парою'
SettingsChangeMinutesBeforeLessonsNotification = '🛎️ Змінити час сповіщення перед парами'
SettingsBack = '🔙 Назад'
settingsKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [SettingsChangeSubGroup, SettingsChangeMinutesBeforeLessonNotification,
           SettingsChangeMinutesBeforeLessonsNotification, SettingsBack]
settingsKeyboard.add(*buttons)

SubGroupOne = 'Перша'
SubGroupTwo = 'Друга'
subGroupsKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [SubGroupOne, SubGroupTwo]
subGroupsKeyboard.add(*buttons)

BroadcastBack = 'Назад'
broadcastKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [BroadcastBack]
broadcastKeyboard.add(*buttons)
