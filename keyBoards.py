from aiogram import types

LogIn = 'LogIn'
Profile = 'Profile'
Marks = 'Marks'
Settings = 'Settings'

mainKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [LogIn, Profile, Marks, Settings]
mainKeyboard.add(*buttons)