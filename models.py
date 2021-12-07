from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegramId = Column(Integer, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)

    groupName = Column(String)
    subGroup = Column(Integer, default=0)

    learnUserName = Column(String)
    learnPassword = Column(String)
    learnCookie = Column(String)
    learnSubscribed = Column(Boolean, default=True)


engine = create_engine("sqlite:///database.sqlite3")
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
    user = getUserByTelegramId(telegramId)
    setattr(user, 'learnUserName', userName)
    setattr(user, 'learnPassword', password)
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
