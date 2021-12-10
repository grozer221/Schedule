import enum
import os

import cryptocode
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Boolean, create_engine, Text, Enum
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


engine = create_engine(
    x.replace("mysql://", "mysql+pymysql://", 1) if (x := os.environ.get('JAWSDB_URL')) else os.getenv('LOCAL_DB'))
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
connection = engine.connect()

Base.metadata.create_all(engine)


def getUserByTelegramId(telegramId):
    return session.query(User).filter_by(telegramId=telegramId)[0]


def getUsers():
    return session.query(User).all()


def createUserIfNessessary(telegramId: int, firstName: str, lastName: str, userName: str):
    count = 0
    for user in session.query(User).filter_by(telegramId=telegramId):
        count += 1
    if count == 0:
        user = User(telegramId=telegramId, first_name=firstName,
                    last_name=lastName, username=userName)
        session.add(user)
        session.commit()
    return None


def updateLearnUserNameAndPassword(telegramId: int, userName: str, password: str):
    cryptedPassword = cryptocode.encrypt(password, os.getenv('API_TOKEN'))
    user = getUserByTelegramId(telegramId)
    setattr(user, 'learnUserName', userName)
    setattr(user, 'learnPassword', cryptedPassword)
    session.commit()


def updateUserCookie(telegramId: int, cookies: str):
    user = getUserByTelegramId(telegramId)
    setattr(user, 'learnCookie', cookies)
    session.commit()


def updateUserGroup(telegramId: int, groupName: str):
    user = getUserByTelegramId(telegramId)
    setattr(user, 'groupName', groupName)
    session.commit()


def updateUserSubGroup(telegramId: int, subGroup: int):
    user = getUserByTelegramId(telegramId)
    setattr(user, 'subGroup', subGroup)
    session.commit()


def updateUserMinutesBeforeLessonsNotification(telegramId: int, minutesBeforeLessonsNoification: int):
    user = getUserByTelegramId(telegramId)
    setattr(user, 'minutesBeforeLessonsNotification', minutesBeforeLessonsNoification)
    session.commit()


def updateUserMinutesBeforeLessonNotification(telegramId: int, minutesBeforeLessonNoification: int):
    user = getUserByTelegramId(telegramId)
    setattr(user, 'minutesBeforeLessonNotification', minutesBeforeLessonNoification)
    session.commit()


def logoutUser(telegramId: int):
    user = getUserByTelegramId(telegramId)
    setattr(user, 'learnUserName', '')
    setattr(user, 'learnPassword', '')
    setattr(user, 'learnCookie', '')
    session.commit()
