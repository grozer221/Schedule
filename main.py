import asyncio
import datetime
import logging
import os

import aioschedule
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from dotenv import load_dotenv

from States import *
from keyBoards import mainKeyboard, Profile, Marks, Settings, settingsKeyboard, SettingsChangeSubGroup, \
    subGroupsKeyboard, SubGroupTwo, SubGroupOne, Schedule, scheduleKeyboard, ScheduleForToday, ScheduleForTomorrow, \
    ScheduleForWeek, ScheduleForTwoWeek, LogOut
from models import createUserIfNessessary, updateLearnUserNameAndPassword, getUsers, updateUserSubGroup, \
    getUserByTelegramId, logoutUser
from requestsZTU import getProfile, getMarks, loginInLearn, getScheduleWithLinksForToday, getScheduleForToday, \
    getScheduleForWeek, getScheduleForTwoWeek, isAuth

load_dotenv()

loop = asyncio.get_event_loop()
bot = Bot(token=os.getenv('API_TOKEN'), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


async def buildSchedule():
    global schedules
    schedules = {}
    users = getUsers()
    for user in users:
        schedules[user.telegramId] = getScheduleWithLinksForToday(user.telegramId)
    print("!!!Schedule is built!!!")


async def notify():
    print('!!!Notify!!!')
    global schedules
    for telegramId in schedules:
        if schedules[telegramId] is not None:
            for subject in schedules[telegramId]:
                currentTimePlus10 = (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime("%H:%M")
                subjectTime = subject['time'].split('-')[0]
                if currentTimePlus10 == subjectTime:
                    await bot.send_message(telegramId,
                                           f'<strong>{subject["name"]}</strong> / {subject["cabinet"]} / через 10 хвилин / {subject["link"]}')


async def buildScheduleAndNotify():
    await buildSchedule()
    await notify()


async def scheduler():
    aioschedule.every().day.at('08:20').do(buildScheduleAndNotify)
    aioschedule.every().day.at('09:50').do(buildScheduleAndNotify)
    aioschedule.every().day.at('11:30').do(buildScheduleAndNotify)
    aioschedule.every().day.at('13:20').do(buildScheduleAndNotify)
    aioschedule.every().day.at('14:50').do(buildScheduleAndNotify)
    aioschedule.every().day.at('16:20').do(buildScheduleAndNotify)
    aioschedule.every().day.at('17:50').do(buildScheduleAndNotify)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def onStartup(_):
    asyncio.create_task(scheduler())
    await buildScheduleAndNotify()


schedules = []


@dp.message_handler(Command("start"), state=None)
async def start(message: types.Message, state: FSMContext):
    print(f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: /start')
    await state.finish()
    createUserIfNessessary(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                           message.from_user.username)
    result = isAuth(message.from_user.id)
    if result == True:
        await message.answer("Виберіть дію:", reply_markup=mainKeyboard)
    else:
        await writeUserName(message)


@dp.message_handler(lambda message: message.text == Schedule)
async def schedule(message: types.Message):
    print(f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: schedule')
    await message.answer("Розклад:", reply_markup=scheduleKeyboard)
    await SelectScheduleTypeState.first()


@dp.message_handler(state=SelectScheduleTypeState.ReadScheduleType)
async def readScheduleType(message: types.Message, state: FSMContext):
    scheduleType = message.text
    user = getUserByTelegramId(message.from_user.id)
    if scheduleType == ScheduleForToday:
        schedule = getScheduleForToday(user.groupName, user.subGroup)
        if type(schedule) == str:
            await message.answer(schedule, reply_markup=mainKeyboard)
        elif type(schedule) == list:
            for subject in schedule:
                await message.answer(
                    f'<strong>{subject["name"]}</strong> / {subject["cabinet"]} / {subject["time"]} / {subject["teacher"].split(" ")[0]}',
                    reply_markup=mainKeyboard)
        else:
            await message.answer('Помилка!!', reply_markup=mainKeyboard)

    elif scheduleType == ScheduleForTomorrow:
        await message.answer("На завтра", reply_markup=mainKeyboard)

    elif scheduleType == ScheduleForWeek:
        schedule = getScheduleForWeek(user.groupName, user.subGroup)
        for day in schedule:
            text = f'📅 <i><strong>{day}</strong></i>  {"🤯" if len(schedule[day]) > 3 else ""}\n'
            for i, subject in enumerate(schedule[day]):
                text += f'<strong>{i + 1}) {subject["name"]}</strong> / {subject["cabinet"]} / {subject["time"]} / {subject["teacher"]}\n'
            await message.answer(text, reply_markup=mainKeyboard)

    elif scheduleType == ScheduleForTwoWeek:
        schedule = getScheduleForTwoWeek(user.groupName, user.subGroup)
        for i, keyWeek in enumerate(schedule):
            await message.answer(f'🆘                   <strong>{keyWeek}</strong>', reply_markup=mainKeyboard)
            for keyDay in schedule[keyWeek]:
                text = f'📅 <i><strong>{keyDay}</strong></i>  {"🤯" if len(schedule[keyWeek][keyDay]) > 3 else ""}\n'
                for j, subject in enumerate(schedule[keyWeek][keyDay]):
                    text += f'<strong>{j + 1}) {subject["name"]}</strong> / {subject["cabinet"]} / {subject["time"]} / {subject["teacher"]}\n'
                await message.answer(text, reply_markup=mainKeyboard)
            if i != len(schedule) - 1:
                await message.answer(f'ᅠᅠᅠᅠᅠᅠ                   ᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠ', reply_markup=mainKeyboard)

    else:
        await message.answer("Не правильно вибраний розклад!", reply_markup=mainKeyboard)
    await state.finish()


@dp.message_handler(lambda message: message.text == Profile)
async def profile(message: types.Message):
    print(f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: profile')
    await message.answer(getProfile(message.from_user.id))


@dp.message_handler(lambda message: message.text == Marks)
async def marks(message: types.Message):
    print(f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: marks')
    for msg in getMarks(message.from_user.id):
        await message.answer(msg)


async def writeUserName(message: types.Message):
    print(f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: login')
    await message.answer("<strong>Авторизація в особистому кабінеті</strong>", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Learn логін:", reply_markup=types.ReplyKeyboardRemove())
    await LearnLogInState.first()


@dp.message_handler(state=LearnLogInState.ReadUserName)
async def writePassword(message: types.Message, state: FSMContext):
    learnUserName = message.text
    await message.delete()
    async with state.proxy() as data:
        data['learnUserName'] = learnUserName

    await message.answer("Learn пароль:", reply_markup=types.ReplyKeyboardRemove())
    await LearnLogInState.next()


@dp.message_handler(state=LearnLogInState.ReadPassword)
async def submitLogin(message: types.Message, state: FSMContext):
    learnPassword = message.text
    await message.delete()
    async with state.proxy() as data:
        learnUserName = data["learnUserName"]

    await state.finish()

    result = loginInLearn(message.from_user.id, learnUserName, learnPassword)
    if result == True:
        # key = Fernet.generate_key()
        # fernet = Fernet(key)
        # ctyptedPassword = fernet.encrypt(learnPassword.encode())
        updateLearnUserNameAndPassword(message.from_user.id, learnUserName, learnPassword)
        await message.answer(f'Ви успішно увійшли в особистий кабінет', reply_markup=mainKeyboard)
    else:
        await message.answer(f'Не правильний логін або пароль')
        await writeUserName(message)


@dp.message_handler(lambda message: message.text == Settings)
async def settings(message: types.Message):
    print(f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: settings')
    await message.answer("Виберіть налаштування:", reply_markup=settingsKeyboard)
    await SettingsState.first()


@dp.message_handler(state=SettingsState.ReadSettingsAction)
async def readSettingsAction(message: types.Message):
    settingAction = message.text
    if settingAction == SettingsChangeSubGroup:
        await message.answer("Виберіть підгрупу:", reply_markup=subGroupsKeyboard)
        await ChangeSubGroupState.first()
    else:
        await message.answer("Не правильно вибране налаштування!", reply_markup=mainKeyboard)
        await settings(message)


@dp.message_handler(state=ChangeSubGroupState.ReadSubGroup)
async def changeSubGroup(message: types.Message, state: FSMContext):
    await state.finish()
    subGroup = message.text
    if subGroup != SubGroupOne and subGroup != SubGroupTwo:
        await message.answer("Не правильно вибрана підгрупа!", reply_markup=mainKeyboard)
        await message.answer("Виберіть підгрупу:", reply_markup=subGroupsKeyboard)
        await ChangeSubGroupState.first()
    else:
        if subGroup == SubGroupOne:
            subGroup = 1
        else:
            subGroup = 2

        updateUserSubGroup(message.from_user.id, subGroup)
        await message.answer('Групу успішно змінено', reply_markup=mainKeyboard)


@dp.message_handler(lambda message: message.text == LogOut)
async def logout(message: types.Message):
    print(f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: logout')
    logoutUser(message.from_user.id)
    await message.answer("Ви вийшли із особистого кабінету")
    await writeUserName(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=onStartup)
