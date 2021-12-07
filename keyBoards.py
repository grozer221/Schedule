from aiogram import types

LogIn = 'Увійти'
Profile = 'Профіль'
Marks = 'Оцінки'
Settings = 'Налаштування'

mainKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [LogIn, Profile, Marks, Settings]
mainKeyboard.add(*buttons)

SettingsChangeSubGroup = 'Змінити підгрупу'
settingsKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [SettingsChangeSubGroup]
settingsKeyboard.add(*buttons)


SubGroupOne = 'Перша'
SubGroupTwo = 'Друга'
subGroupsKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [SubGroupOne, SubGroupTwo]
subGroupsKeyboard.add(*buttons)