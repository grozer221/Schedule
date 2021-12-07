import json

import requests
from bs4 import BeautifulSoup

from models import updateUserCookie, getUserByTelegramId, updateUserGroup

urlMain = 'https://cabinet.ztu.edu.ua'
urlLogin = urlMain + '/site/login'
urlSchedule = urlMain + '/site/schedule'
urlRozkladGroup = 'https://rozklad.ztu.edu.ua/schedule/group/'


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
    soup = BeautifulSoup(responseLoginPost.text)
    tableProfile = soup.find('table', {'class': 'table table-bordered'})
    groupRowItem = tableProfile.find_all('tr')[4]
    groupName = groupRowItem.find('td').text.strip().lstrip()
    updateUserGroup(telegramId, groupName)
    cookies = [
        {'domain': cookie.domain, 'name': cookie.name, 'path': cookie.path, 'value': cookie.value}
        for cookie in reqSession.cookies
    ]
    updateUserCookie(telegramId, json.dumps(cookies))
    return True


def getProfile(telegramId: int):
    user = getUserByTelegramId(telegramId)
    if user.learnCookie is None or user.learnCookie == '':
        return 'Увійдіть в особистий кабінет'
    reqSession = requests.Session()
    for cookie in json.loads(user.learnCookie):
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
    if user.learnCookie is None or user.learnCookie == '':
        return ['Увійдіть в особистий кабінет']
    reqSession = requests.Session()
    for cookie in json.loads(user.learnCookie):
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
            subjectMark = markRowItem.find("span", {"class": "points"}).text
            message += f'<strong>{subjectName}:</strong>{subjectMark}\n'
        message += '\n'
        result.append(message)
        count += 1
    return result


def getScheduleForToday(telegramId: int):
    user = getUserByTelegramId(telegramId)
    if user.learnCookie:
        reqSession = requests.Session()
        for cookie in json.loads(user.learnCookie):
            reqSession.cookies.set(**cookie)
        responseSchedule = reqSession.get(urlSchedule)
        soup = BeautifulSoup(responseSchedule.text)
        pairItems = soup.find_all('div', {'class': 'pair'})
        subjects = []
        for pairItem in pairItems:
            subject = {}
            subject['link'] = pairItem.find('div', {'style': 'font-size:1.5em;'}).text.rstrip().lstrip()
            subject['time'] = pairItem.find_all('div', {'class': 'time'})[1].text
            subjectTypes = pairItem.find_all('div', {'class': 'type'})
            subject['cabinet'] = subjectTypes[1].text
            subject['teacher'] = subjectTypes[2].text
            subject['name'] = pairItem.find('div', {'class': 'subject'}).text.rstrip().lstrip()
            subjects.append(subject)

        responseRozklad = reqSession.get(urlRozkladGroup + user.groupName)
        soup = BeautifulSoup(responseRozklad.text)
        rozkladPairItems = soup.find_all('td', {'class': 'content selected'})
        rozkladSubjects = []
        for pairItem in rozkladPairItems:
            if pairItem.text.rstrip().lstrip() == '':
                continue

            subject = {}
            subject['time'] = pairItem['hour']
            try:
                subjectItem = pairItem.find_all('div', {'class': 'one'})[user.subGroup - 1]
            except:
                subjectItem = pairItem
            if subjectItem.text.rstrip().lstrip() == '':
                continue
            subject['cabinet'] = subjectItem.find('span', {'class': 'room'}).text.rstrip().lstrip()
            subject['teacher'] = subjectItem.find('div', {'class': 'teacher'}).text
            subject['name'] = subjectItem.find('div', {'class': 'subject'}).text
            rozkladSubjects.append(subject)

        scheduleResult = []
        for subject in subjects:
            for rozkladSubject in rozkladSubjects:
                if subject['time'] != rozkladSubject['time'] or subject['teacher'] != rozkladSubject['teacher']:
                    continue
                scheduleResult.append(subject)
        return scheduleResult
    return None
