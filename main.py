import asyncio
import os
from datetime import datetime, timedelta

import aioschedule
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from dotenv import load_dotenv

from antiFlood import antiFlood
from States import *
from keyBoards import mainKeyboard, Profile, Marks, Settings, settingsKeyboard, SettingsChangeSubGroup, \
    subGroupsKeyboard, SubGroupTwo, SubGroupOne, ScheduleForToday, ScheduleForTomorrow, \
    ScheduleForTwoWeeks, LogOut, More, moreKeyboard, Back, SettingsChangeMinutesBeforeLessonsNotification, \
    SettingsChangeMinutesBeforeLessonNotification, SettingsBack, broadcastKeyboard, BroadcastBack
from models import createUserIfNessessary, updateLearnUserNameAndPassword, getUsers, updateUserSubGroup, \
    getUserByTelegramId, logoutUser, updateUserMinutesBeforeLessonsNotification, \
    updateUserMinutesBeforeLessonNotification, Role, createConnection
from requestsZTU import getProfile, getMarks, loginInLearn, getScheduleWithLinksForToday, getScheduleForTwoWeek, isAuth, \
    getScheduleForTomorrow, getNewSubjectLinkForUser

load_dotenv()

loop = asyncio.get_event_loop()
bot = Bot(token=os.getenv('API_TOKEN'), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)
schedules = []


async def buildSchedule():
    global schedules
    schedules = {}
    for user in await getUsers():
        schedules[user.telegramId] = await getScheduleWithLinksForToday(user.telegramId)
    print("!!!Schedule is built!!!")


async def updateScheduleForUser(telegramId: int):
    global schedules
    schedules[telegramId] = await getScheduleWithLinksForToday(telegramId)


async def notify():
    global schedules
    for telegramId in schedules:
        if schedules[telegramId] is not None and len(schedules[telegramId]) > 0:
            user = await getUserByTelegramId(telegramId)
            # notification before lessons
            currentTimeCustomPlus = (datetime.now() + timedelta(
                minutes=user.minutesBeforeLessonsNotification)).strftime("%H:%M")
            if schedules[telegramId][0]['time'].split('-')[0] == currentTimeCustomPlus:
                message = f'Через {user.minutesBeforeLessonsNotification} хвилин початок пар'
                print(f'#{user.telegramId} {user.first_name} {user.last_name} @{user.username}: {message}')
                await bot.send_message(telegramId, message)
            for subject in schedules[telegramId]:
                # notification before lesson
                subjectStartTime = subject['time'].split('-')[0]
                currentDateTime = datetime.now()
                currentTime = datetime.now().strftime("%H:%M")
                currentTimeCustomPlus = (
                        currentDateTime + timedelta(minutes=user.minutesBeforeLessonNotification)).strftime("%H:%M")
                if subjectStartTime == currentTimeCustomPlus:
                    message = f'<strong>{subject["name"]}</strong> / {subject["cabinet"]} / через {user.minutesBeforeLessonNotification} хвилин / {subject["teacher"]} / {subject["link"]}'
                    print(f'#{user.telegramId} {user.first_name} {user.last_name} @{user.username}: {message}')
                    await bot.send_message(telegramId, message)

                subjectStartTimeParsed = datetime.strptime(subjectStartTime, "%H:%M")
                subjectStartTimePlus15 = (subjectStartTimeParsed + timedelta(minutes=15)).strftime("%H:%M")
                # notification teacher added link
                if 'Викладач ще не надав інформацію' in subject['link'] \
                        and currentTimeCustomPlus > subjectStartTime and currentTime < subjectStartTimePlus15:
                    newSubjectLink = await getNewSubjectLinkForUser(user.telegramId, subjectStartTime)
                    if newSubjectLink is not None and newSubjectLink != subject['link']:
                        subject['link'] = newSubjectLink
                        message = f'Викладач {subject["teacher"]} додав посилання / <strong>{subject["name"]}</strong> / {subject["cabinet"]} / {subject["time"]} / {subject["link"]}'
                        print(f'#{user.telegramId} {user.first_name} {user.last_name} @{user.username}: {message}')
                        await bot.send_message(telegramId, message)


async def scheduler():
    aioschedule.every().minute.do(notify)
    timesNotification = ['08:00', '09:30', '11:10', '13:00', '14:30', '16:00', '17:30']
    [aioschedule.every().day.at(timeNotification).do(buildSchedule) for timeNotification in timesNotification]
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def onStartup(_):
    await createConnection()
    asyncio.create_task(scheduler())
    await buildSchedule()
    await notify()
    print('BOT has been started')


@dp.message_handler(Command("start"), state=None)
@dp.throttled(antiFlood, rate=2)
async def start(message: types.Message, state: FSMContext):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: /start')
    await state.finish()
    await createUserIfNessessary(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                                 message.from_user.username)
    result = await isAuth(message.from_user.id)
    if result == True:
        await message.answer("Розклад:", reply_markup=mainKeyboard)
    else:
        await writeUserName(message)


@dp.message_handler(Command("info"), state=None)
@dp.throttled(antiFlood, rate=2)
async def info(message: types.Message, state: FSMContext):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: /info')
    await message.answer(
        'Здоров. Я бот розкладу Житомирської політехніки. '
        'Я можу показати тобі інформацію з твого особистого кабінету студента, розклад та також присилати сповіщення перед початком пар.\n\n'
        'Склад "Віталік текнолоджі":\n'
        '@grozer - кодіровщик,\n'
        '@EgorWasBorn - піар менеджер, тестувальник,\n'
        '@ngprdcr - тестувальник, ректор,\n'
        '@Programmer_ZTU - тестувальник.'
    )
    await start(message, state)


@dp.message_handler(Command("broadcast"), state=None)
@dp.throttled(antiFlood, rate=2)
async def broadcast(message: types.Message, state: FSMContext):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: /broadcast')
    await message.answer('Повідомлення для розсилки:', reply_markup=broadcastKeyboard)
    await BroadcastState.first()


@dp.message_handler(state=BroadcastState.ReadBroadcastText)
@dp.throttled(antiFlood, rate=2)
async def readBroadcastText(message: types.Message, state: FSMContext):
    user = await getUserByTelegramId(message.from_user.id)
    if user.role == Role.admin:
        messageText = message.text
        if messageText == BroadcastBack:
            await start(message, state)
        else:
            for user in await getUsers():
                await bot.send_message(user.telegramId, messageText)
        await state.finish()
    else:
        await message.answer('‼️ Недостатньо прав ‼️')
        await state.finish()
    await start(message, state)


@dp.message_handler(lambda message: message.text == ScheduleForToday)
@dp.throttled(antiFlood, rate=2)
async def scheduleForToday(message: types.Message, state: FSMContext):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: schedule today')
    schedule = await getScheduleWithLinksForToday(message.from_user.id)
    if len(schedule) == 0:
        await message.answer('🎉🎉 Пар сьогодні немає 🎉🎉')
        await message.answer_sticker(r'CAACAgQAAxkBAAEDdiNhtJU0pIxJfgW3X4ArXFE-wi1ZfAACRAEAAqghIQa6r-zNMwJb3iME')
    else:
        for subject in schedule:
            await message.answer(
                f'<strong>{subject["name"]}</strong> / 🚪 {subject["type"]} {subject["cabinet"]} / ⏱️{subject["time"]} / 👨‍🏫 {subject["teacher"]} / 🔗 {subject["link"]}',
                reply_markup=mainKeyboard)
    await start(message, state)


@dp.message_handler(lambda message: message.text == ScheduleForTomorrow)
@dp.throttled(antiFlood, rate=2)
async def scheduleForTomorrow(message: types.Message, state: FSMContext):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: schedule tomorrow')

    user = await getUserByTelegramId(message.from_user.id)
    schedule = await getScheduleForTomorrow(user.groupName, user.subGroup)
    for subject in schedule:
        await message.answer(
            f'<strong>{subject["name"]}</strong> / 🚪 {subject["type"]} {subject["cabinet"]} / ⏱️{subject["time"]} / 👨‍🏫 {subject["teacher"]}')
    await start(message, state)


@dp.message_handler(lambda message: message.text == ScheduleForTwoWeeks)
@dp.throttled(antiFlood, rate=2)
async def scheduleForTwoWeeks(message: types.Message, state: FSMContext):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: schedule 2 weeks')
    user = await getUserByTelegramId(message.from_user.id)
    schedule = await getScheduleForTwoWeek(user.groupName, user.subGroup)
    for keyWeek in schedule:
        await message.answer(f'🆘🆘🆘🆘🆘🆘🆘🆘  <strong>{keyWeek}</strong>  🆘🆘🆘🆘🆘🆘🆘🆘',
                             reply_markup=mainKeyboard)
        for keyDay in schedule[keyWeek]:
            text = f'📅 <i><strong>{keyDay}</strong></i>  {"🤯🧨" if len(schedule[keyWeek][keyDay]) > 3 else ""}\n'
            for i, subject in enumerate(schedule[keyWeek][keyDay]):
                text += f'<strong>{i + 1}) {subject["name"]}</strong> / {subject["type"]} {subject["cabinet"]} / ⏱️{subject["time"]} / 👨‍🏫 {subject["teacher"]}\n'
            await message.answer(text)
    await start(message, state)


@dp.message_handler(lambda message: message.text == More)
@dp.throttled(antiFlood, rate=2)
async def more(message: types.Message):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: more')
    await message.answer("Більше:", reply_markup=moreKeyboard)


@dp.message_handler(lambda message: message.text == Back, state=None)
@dp.throttled(antiFlood, rate=2)
async def back(message: types.Message, state: FSMContext):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: back')
    await start(message, state)


@dp.message_handler(lambda message: message.text == Profile)
@dp.throttled(antiFlood, rate=2)
async def profile(message: types.Message):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: profile')
    await message.answer(await getProfile(message.from_user.id))


@dp.message_handler(lambda message: message.text == Marks)
@dp.throttled(antiFlood, rate=2)
async def marks(message: types.Message):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: marks')
    for msg in await getMarks(message.from_user.id):
        await message.answer(msg)


async def writeUserName(message: types.Message):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: login')
    await createUserIfNessessary(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                                 message.from_user.username)
    await message.answer("<strong>Авторизація в особистому кабінеті</strong>", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Learn логін:", reply_markup=types.ReplyKeyboardRemove())
    await LearnLogInState.first()


@dp.message_handler(state=LearnLogInState.ReadUserName)
@dp.throttled(antiFlood, rate=2)
async def writePassword(message: types.Message, state: FSMContext):
    learnUserName = message.text
    await message.delete()
    async with state.proxy() as data:
        data['learnUserName'] = learnUserName

    await message.answer("Learn пароль:", reply_markup=types.ReplyKeyboardRemove())
    await LearnLogInState.next()


@dp.message_handler(state=LearnLogInState.ReadPassword)
@dp.throttled(antiFlood, rate=2)
async def submitLogin(message: types.Message, state: FSMContext):
    learnPassword = message.text
    await message.delete()
    async with state.proxy() as data:
        learnUserName = data["learnUserName"]

    await state.finish()

    result = await loginInLearn(message.from_user.id, learnUserName, learnPassword)
    if result == True:
        await updateLearnUserNameAndPassword(message.from_user.id, learnUserName, learnPassword)
        await message.answer(f'✅✅ Ви успішно увійшли в особистий кабінет ✅✅')
        await start(message, state)
    else:
        await message.answer(f'‼️‼️ Не правильний логін або пароль ‼️‼️')
        await writeUserName(message)


@dp.message_handler(lambda message: message.text == Settings)
@dp.throttled(antiFlood, rate=2)
async def settings(message: types.Message):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: settings')
    await message.answer("Виберіть налаштування:", reply_markup=settingsKeyboard)
    await SettingsState.first()


@dp.message_handler(state=SettingsState.ReadSettingsAction)
@dp.throttled(antiFlood, rate=2)
async def readSettingsAction(message: types.Message, state: FSMContext):
    settingAction = message.text
    if settingAction == SettingsChangeSubGroup:
        await message.answer("Виберіть підгрупу:", reply_markup=subGroupsKeyboard)
        await ChangeSubGroupState.first()
    elif settingAction == SettingsChangeMinutesBeforeLessonsNotification:
        await message.answer("Введіть час сповіщення перед парами (1-90 хвилин):",
                             reply_markup=types.ReplyKeyboardMarkup())
        await ChangeMinutesBeforeLessonsNotificationState.first()
    elif settingAction == SettingsChangeMinutesBeforeLessonNotification:
        await message.answer("Введіть час сповіщення перед парою (1-30 хвилин):",
                             reply_markup=types.ReplyKeyboardMarkup())
        await ChangeMinutesBeforeLessonNotificationState.first()
    elif settingAction == SettingsBack:
        await state.finish()
        await more(message)
    else:
        await message.answer("Не правильно вибране налаштування!", reply_markup=mainKeyboard)
        await settings(message)


@dp.message_handler(state=ChangeSubGroupState.ReadSubGroup)
@dp.throttled(antiFlood, rate=2)
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

        await updateUserSubGroup(message.from_user.id, subGroup)
        await updateScheduleForUser(message.from_user.id)
        await message.answer('Групу успішно змінено')
        await settings(message)


@dp.message_handler(state=ChangeMinutesBeforeLessonsNotificationState.ReadMinutesBeforeLessonsNotification)
@dp.throttled(antiFlood, rate=2)
async def changeMinutesBeforeLessonsNotification(message: types.Message, state: FSMContext):
    await state.finish()
    try:
        minutesBeforeLessonsNotification = int(message.text)
        if type(minutesBeforeLessonsNotification) is not int or minutesBeforeLessonsNotification < 1 or minutesBeforeLessonsNotification > 90:
            await message.answer('Не правильно введене значення!')
            await message.answer("Введіть час сповіщення перед парами (1-90 хвилин):",
                                 reply_markup=types.ReplyKeyboardMarkup())
            await ChangeMinutesBeforeLessonsNotificationState.first()
        else:
            await updateUserMinutesBeforeLessonsNotification(message.from_user.id, minutesBeforeLessonsNotification)
            await message.answer(
                f'Час сповіщення перед парами успішно змінено на {minutesBeforeLessonsNotification} хвилин',
                reply_markup=mainKeyboard)
            await settings(message)
    except:
        await message.answer('Не правильно введене значення!')
        await message.answer("Введіть час сповіщення перед парами (1-90 хвилин):",
                             reply_markup=types.ReplyKeyboardMarkup())
        await ChangeMinutesBeforeLessonsNotificationState.first()


@dp.message_handler(state=ChangeMinutesBeforeLessonNotificationState.ReadMinutesBeforeLessonNotification)
@dp.throttled(antiFlood, rate=2)
async def changeMinutesBeforeLessonNotification(message: types.Message, state: FSMContext):
    await state.finish()
    try:
        minutesBeforeLessonNotification = int(message.text)
        if type(minutesBeforeLessonNotification) is not int or minutesBeforeLessonNotification < 1 or minutesBeforeLessonNotification > 30:
            await message.answer('Не правильно введене значення!')
            await message.answer("Введіть час сповіщення перед парою (1-30 хвилин):",
                                 reply_markup=types.ReplyKeyboardMarkup())
            await ChangeMinutesBeforeLessonNotificationState.first()
        else:
            await updateUserMinutesBeforeLessonNotification(message.from_user.id, minutesBeforeLessonNotification)
            await message.answer(
                f'Час сповіщення перед парою успішно змінено на {minutesBeforeLessonNotification} хвилин',
                reply_markup=mainKeyboard)
            await settings(message)
    except:
        await message.answer('Не правильно введене значення!')
        await message.answer("Введіть час сповіщення перед парою (1-30 хвилин):",
                             reply_markup=types.ReplyKeyboardMarkup())
        await ChangeMinutesBeforeLessonsNotificationState.first()


@dp.message_handler(lambda message: message.text == LogOut)
@dp.throttled(antiFlood, rate=2)
async def logout(message: types.Message):
    print(
        f'#{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}: logout')
    await logoutUser(message.from_user.id)
    await message.answer("⚠️⚠️ Ви вийшли із особистого кабінету ⚠️⚠️")
    await writeUserName(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=onStartup)
