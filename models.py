import enum
import os

import cryptocode
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Boolean, Text, Enum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

Base = declarative_base()


class Role(enum.Enum):
    admin = 'admin'
    user = 'user'


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegramId = Column(Integer, unique=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(Enum(Role), default=Role.user)

    groupName = Column(String(100))
    subGroup = Column(Integer, default=1)

    learnUserName = Column(String(100))
    learnPassword = Column(String(100))
    learnCookie = Column(Text)
    learnSubscribed = Column(Boolean, default=True)

    minutesBeforeLessonNotification = Column(Integer, default=10)
    minutesBeforeLessonsNotification = Column(Integer, default=60)


async def createConnection():
    engine = create_async_engine(
        x.replace("mysql://", "mysql+asyncmy://", 1) if (x := os.environ.get('JAWSDB_URL')) else os.getenv('LOCAL_DB'))

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    global async_session
    async_session = AsyncSession(engine, expire_on_commit=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def getUserByTelegramId(telegramId):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegramId == telegramId))
            return result.scalars().first()


async def getUsers():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User))
            return result.scalars().all()


async def createUserIfNessessary(telegramId: int, firstName: str, lastName: str, userName: str):
    async with async_session() as session:
        async with session.begin():
            user = await getUserByTelegramId(telegramId)
            if user is None:
                user = User(telegramId=telegramId, first_name=firstName,
                            last_name=lastName, username=userName)
                session.add(user)
                await session.commit()


async def updateLearnUserNameAndPassword(telegramId: int, userName: str, password: str):
    async with async_session() as session:
        async with session.begin():
            cryptedPassword = cryptocode.encrypt(password, os.getenv('CRYPT_KEY'))
            result = await session.execute(select(User).where(User.telegramId == telegramId))
            user = result.scalars().first()
            user.learnUserName = userName
            user.learnPassword = cryptedPassword
            await session.commit()


async def updateUserCookie(telegramId: int, cookies: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegramId == telegramId))
            user = result.scalars().first()
            user.learnCookie = cookies
            await session.commit()


async def updateUserGroup(telegramId: int, groupName: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegramId == telegramId))
            user = result.scalars().first()
            user.groupName = groupName
            await session.commit()


async def updateUserSubGroup(telegramId: int, subGroup: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegramId == telegramId))
            user = result.scalars().first()
            user.subGroup = subGroup
            await session.commit()


async def updateUserMinutesBeforeLessonsNotification(telegramId: int, minutesBeforeLessonsNoification: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegramId == telegramId))
            user = result.scalars().first()
            user.minutesBeforeLessonsNotification = minutesBeforeLessonsNoification
            await session.commit()


async def updateUserMinutesBeforeLessonNotification(telegramId: int, minutesBeforeLessonNoification: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegramId == telegramId))
            user = result.scalars().first()
            user.minutesBeforeLessonNotification = minutesBeforeLessonNoification
            await session.commit()


async def logoutUser(telegramId: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegramId == telegramId))
            user = result.scalars().first()
            if user is not None:
                user.learnUserName = ''
                user.learnPassword = ''
                user.learnCookie = ''
                await session.commit()
