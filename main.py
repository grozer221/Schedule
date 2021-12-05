import asyncio
import logging
import os

import aioschedule
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from dotenv import load_dotenv

from LearnLogInState import *
from keyBoards import mainKeyboard, Profile, Marks, LogIn
from models import createUserIfNessessary, updateLearnUserNameAndPassword
from requestsZTU import getProfile, getMarks, loginInLearn

load_dotenv()

loop = asyncio.get_event_loop()
bot = Bot(token=os.getenv('API_TOKEN'), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


@dp.message_handler(Command("start"), state=None)
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Виберіть дію:", reply_markup=mainKeyboard)
    createUserIfNessessary(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                           message.from_user.username)


@dp.message_handler(lambda message: message.text == Profile)
async def profile(message: types.Message):
    await message.answer(getProfile(message.from_user.id))


@dp.message_handler(lambda message: message.text == Marks)
async def marks(message: types.Message):
    for msg in getMarks(message.from_user.id):
        await message.answer(msg)


@dp.message_handler(lambda message: message.text == LogIn)
async def writeUserName(message: types.Message):
    await message.answer("Learn логін:", reply_markup=types.ReplyKeyboardRemove())
    await LearnLogInState.first()


@dp.message_handler(state=LearnLogInState.ReadUserName)
async def writePassword(message: types.Message, state: FSMContext):
    learnUserName = message.text
    async with state.proxy() as data:
        data['learnUserName'] = learnUserName

    await message.answer("Learn пароль:", reply_markup=types.ReplyKeyboardRemove())
    await LearnLogInState.next()


@dp.message_handler(state=LearnLogInState.ReadPassword)
async def submitLogin(message: types.Message, state: FSMContext):
    learnPassword = message.text
    async with state.proxy() as data:
        learnUserName = data["learnUserName"]

    updateLearnUserNameAndPassword(message.from_user.id, learnUserName, learnPassword)
    await state.finish()
    result = loginInLearn(message.from_user.id, learnUserName, learnPassword)
    if result == True:
        await message.answer(f'Ви успішно увійшли в особистий кабінет', reply_markup=mainKeyboard)
    else:
        await message.answer(f'Не правильний логін або пароль', reply_markup=mainKeyboard)



@dp.message_handler(Command('Schedule'))
async def schedule(message: types.Message):
    pass


async def notify():
    print("It's noon!")


async def scheduler():
    aioschedule.every().day.at('16:43').do(notify)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def onStartup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=onStartup)
