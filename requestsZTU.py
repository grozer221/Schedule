import json

import requests
from bs4 import BeautifulSoup

from models import updateUserCookie, getUserByTelegramId, updateUserGroup

urlMain = 'https://cabinet.ztu.edu.ua'
urlLogin = urlMain + '/site/login'
urlSchedule = urlMain + '/site/schedule'
urlRozkladGroup = 'https://rozklad.ztu.edu.ua/schedule/group/'


def getScheduleByRozkladPairItemsForDay(rozkladPairItems, subGroup: int):
    rozkladSubjects = []
    for pairItem in rozkladPairItems:
        if pairItem.text.rstrip().lstrip() == '':
            continue

        subject = {}
        subject['time'] = pairItem['hour']
        try:
            subjectItem = pairItem.find_all('div', {'class': 'one'})[subGroup - 1]
        except:
            subjectItem = pairItem
        if subjectItem.text.rstrip().lstrip() == '':
            continue
        subject['cabinet'] = subjectItem.find('span', {'class': 'room'}).text.rstrip().lstrip()
        subject['name'] = subjectItem.find('div', {'class': 'subject'}).text
        teacher = subjectItem.find('div', {'class': 'teacher'}).text
        emoji = ''
        if 'Морозов Андрій Васильович' in teacher:
            emoji += ' 🧙'
        if 'Фізвиховання' in subject['name']:
            emoji += ' 🏓'
        if 'Лисогор Юрій Іванович' in teacher:
            emoji += ' 🫖🧑🏻‍🎨'
        if 'Окунькова Оксана Олексіївна' in teacher:
            emoji += ' 🐡'
        if 'Програмування мовою Python' in subject['name']:
            emoji += ' 💩'
        if 'Чижмотря Олексій Володимирович' in teacher:
            emoji += ' 🚷'
        if 'Давидчук Сергій Петрович' in subject['name']:
            emoji += ' 🔫'
        if 'Коротун Ольга Володимирівна' in teacher:
            emoji += ' 🐉'
        if 'Локтікова Тамара Миколаївна' in teacher:
            emoji += ' 0️⃣1️⃣'
        if 'Сугоняк Інна Іванівна' in teacher:
            emoji += ' 💽'
        if 'Колос Катерина Ростиславівна' in teacher:
            emoji += ' 😡'
        if 'Семенець Сергій Петрович' in teacher:
            emoji += ' 🎰'
        if 'Бабій Василь Дмитрович' in teacher:
            emoji += ' 🤸'
        if 'Іноземна мова' in subject['name']:
            emoji += ' 🇺🇸'
        if 'Котенко Володимир Миколайович' in teacher:
            emoji += ' ⚡️'
        if 'Філіпов Валерій Олександрович' in teacher:
            emoji += ' ⚡️'
        if 'Біляк Ірина Валеріївна' in teacher:
            emoji += ' 🐱'
        subject['teacher'] = teacher.split(" ")[0] + emoji

        rozkladSubjects.append(subject)
    return rozkladSubjects


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


def isAuth(telegramId: int):
    user = getUserByTelegramId(telegramId)
    if user is None or user.learnUserName is None or user.learnUserName is '' or user.learnPassword is None or user.learnPassword is '':
        return False
    if user.learnCookie is not None and user.learnCookie != '':
        reqSession = requests.Session()
        for cookie in json.loads(user.learnCookie):
            reqSession.cookies.set(**cookie)
        response = reqSession.get(urlMain)
        if 'Вхід в електронний кабінет студента' in response.text:
            return loginInLearn(user.telegramId, user.learnUserName, user.learnPassword)
        return True
    else:
        return loginInLearn(user.telegramId, user.learnUserName, user.learnPassword)


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


def getScheduleWithLinksForToday(telegramId: int):
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
        rozkladSubjects = getScheduleByRozkladPairItemsForDay(rozkladPairItems, user.subGroup)

        scheduleResult = []
        for subject in subjects:
            for rozkladSubject in rozkladSubjects:
                if subject['time'] != rozkladSubject['time'] or subject['teacher'] != rozkladSubject['teacher']:
                    continue
                scheduleResult.append(subject)
        return scheduleResult
    return None


def getScheduleForToday(groupName: str, subGroup: int):
    responseRozklad = requests.get(urlRozkladGroup + groupName)
    soup = BeautifulSoup(responseRozklad.text)

    rozkladHeaderItem = soup.find('th', {'class': 'selected'})
    rozkladDay = rozkladHeaderItem.find('div', {'class': 'message'}).text
    if 'сьогодні' in rozkladDay:
        rozkladPairItems = soup.find_all('td', {'class': 'content selected'})
        rozkladSubjects = getScheduleByRozkladPairItemsForDay(rozkladPairItems, subGroup)
        return rozkladSubjects
    else:
        return 'Пар сьогодні немає'


def getScheduleFromTable(currentWeekTableItem, subGroup):
    trItems = currentWeekTableItem.find_all('tr')
    thItems = trItems[0].find_all('th')
    tdItems = []
    for trItem in trItems:
        tdRowItems = trItem.find_all('td')
        tdItems.append(tdRowItems)
    schedule = {}
    for j in range(0, len(tdItems[1])):
        scheduleForDay = {}
        scheduleForDayItems = []
        for i in range(1, len(trItems)):
            scheduleForDayItems.append(tdItems[i][j])
        rozkladSubjects = getScheduleByRozkladPairItemsForDay(scheduleForDayItems, subGroup)
        weekDayItem = thItems[j + 1]
        weekDay = weekDayItem.text
        messageItem = weekDayItem.find('div', {'class': 'message'})
        if messageItem is not None:
            weekDay = f"{weekDay.replace(messageItem.text, '')} ({messageItem.text})"
        schedule[weekDay] = rozkladSubjects
    return schedule


def getScheduleForWeek(groupName: str, subGroup: int):
    responseRozklad = requests.get(urlRozkladGroup + groupName)
    soup = BeautifulSoup(responseRozklad.text)
    tableItems = soup.find_all('table', {'class': 'schedule'})
    currentWeekTableItem = None
    for tableItem in tableItems:
        selectedTableHeaderItem = tableItem.find('th', {'class': 'selected'})
        if selectedTableHeaderItem is not None:
            currentWeekTableItem = tableItem

    return getScheduleFromTable(currentWeekTableItem, subGroup)


def getScheduleForTwoWeek(groupName: str, subGroup: int):
    responseRozklad = requests.get(urlRozkladGroup + groupName)
    soup = BeautifulSoup(responseRozklad.text)
    tableItems = soup.find_all('table', {'class': 'schedule'})
    schedule = {}
    for i, tableItem in enumerate(tableItems):
        schedule[f'{i + 1} тиждень'] = getScheduleFromTable(tableItem, subGroup)
    return schedule
