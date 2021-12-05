import json

import requests
from bs4 import BeautifulSoup

from models import updateUserCookie, getUserByTelegramId

urlMain = 'https://cabinet.ztu.edu.ua'
urlLogin = urlMain + '/site/login'


def loginInLearn(telegramId: int, learnUserName: str, learnPassword: str):
    reqSession = requests.Session()
    responeLoginGet = reqSession.get(urlLogin)
    soup = BeautifulSoup(responeLoginGet.text)
    _csrf_frontend = soup.find('input', {'name': '_csrf-frontend'})['value']
    data = {
        '_csrf-frontend': _csrf_frontend,
        'LoginForm[username]': learnUserName,
        'LoginForm[password]': learnPassword,
        'LoginForm[rememberMe]': 1,
    }
    responseLoginPost = reqSession.post(urlLogin, data=data)
    print(responseLoginPost.status_code)
    if "Неправильний логін або пароль" in responseLoginPost.text:
        return False
    cookies = [
        {'domain': cookie.domain, 'name': cookie.name, 'path': cookie.path, 'value': cookie.value}
        for cookie in reqSession.cookies
    ]
    updateUserCookie(telegramId, json.dumps(cookies))
    return True

def getProfile(telegramId: int):
    user = getUserByTelegramId(telegramId)
    if user.learnCoockie is None or user.learnCoockie == '':
        return 'Увійдіть в особистий кабінет'
    reqSession = requests.Session()
    for cookie in json.loads(user.learnCoockie):
        reqSession.cookies.set(**cookie)
    response = reqSession.get(urlMain)
    soup = BeautifulSoup(response.text)
    tableItem = soup.find('table', {'class': 'table table-bordered'})
    rowItems = tableItem.find_all('tr')
    result = ''
    for rowItem in rowItems:
        result += f'<strong>{rowItem.find("th").text}</strong>: {rowItem.find("td").text.rstrip().lstrip()}\n'
    return result


def getMarks(telegramId: int):
    user = getUserByTelegramId(telegramId)
    if user.learnCoockie is None or user.learnCoockie == '':
        return ['Увійдіть в особистий кабінет']
    reqSession = requests.Session()
    for cookie in json.loads(user.learnCoockie):
        reqSession.cookies.set(**cookie)
    response = reqSession.get(urlMain)
    soup = BeautifulSoup(response.text)
    tabPanelItems = soup.find_all('div', {'role': 'tabpanel'})
    print(tabPanelItems)
    navTabsItem = soup.find('ul', {'class': 'nav nav-tabs'})
    tabsItems = navTabsItem.find_all('a', {'role': 'tab'})

    result = []
    count = 0
    for tabItem in tabsItems:
        message = ''
        message += f'<strong>{tabItem.text}</strong>:\n\n'
        markRowItems = tabPanelItems[count].find_all('tr')
        for markRowItem in markRowItems:
            subjectName = markRowItem.find("td", {"class": "text-primary"}).find("b").text
            subjectMark = markRowItem.find("span", {"class": "points offer"}).text
            message += f'<strong>{subjectName}:</strong> {subjectMark}\n'
        message += '\n'
        result.append(message)
        count += 1
    return result