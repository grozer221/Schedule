from aiogram import types

Schedule = 'Розклад'
Profile = 'Профіль'
Marks = 'Оцінки'
Settings = 'Налаштування'
LogOut = 'Вийти'
mainKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [Schedule, Profile, Marks, Settings, LogOut]
mainKeyboard.add(*buttons)

ScheduleForToday = 'На сьогодні'
ScheduleForTomorrow = 'На завтра'
ScheduleForWeek = 'На тиждень'
ScheduleForTwoWeek = 'На 2 тижні'
scheduleKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [ScheduleForToday, ScheduleForTomorrow, ScheduleForWeek, ScheduleForTwoWeek]
scheduleKeyboard.add(*buttons)

SettingsChangeSubGroup = 'Змінити підгрупу'
settingsKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [SettingsChangeSubGroup]
settingsKeyboard.add(*buttons)

SubGroupOne = 'Перша'
SubGroupTwo = 'Друга'
subGroupsKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [SubGroupOne, SubGroupTwo]
subGroupsKeyboard.add(*buttons)
