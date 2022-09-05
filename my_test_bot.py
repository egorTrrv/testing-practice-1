import telebot  # pyTelegramBotAPI
from telegram import ParseMode  # pip install python_telegram_bot
import requests  # for weather

bot = telebot.TeleBot('1644293649:AAFpvIZpkJ3JDagG1tyLDMAv0HsJzJyl2aE')


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "/perevod" + '--- переводит латинские буквы в ASCII символы')
    bot.send_message(message.chat.id, "/calcul" + '--- калькулятор')
    bot.send_message(message.chat.id, "/weather" + '--- узнать погоду в любой точке мира')


@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.text == '/perevod':
        bot.send_message(message.chat.id, "Enter text to translate")
        bot.register_next_step_handler(message, perevod)
    elif message.text == '/weather':
        bot.send_message(message.chat.id, "Enter the city and country")
        bot.send_message(message.chat.id, "For example, 'Moscow, RU'")
        bot.send_message(message.chat.id, "Enter '0' to to stop")
        bot.register_next_step_handler(message, weather)
    elif message.text == '/calcul':
        bot.send_message(message.chat.id, "Enter the task")
        bot.send_message(message.chat.id, "For example, -3*(7-2)+10/2")
        bot.send_message(message.chat.id, "Enter 'stop' to to stop")
        bot.register_next_step_handler(message, calcul)
    else:
        welcome(message)


def perevod(message):
    if message.text.isdigit() is True:
        welcome(message)
        return
    N = 4
    s0 = '';
    s1 = '';
    s2 = '';
    s3 = '';
    s = [s0, s1, s2, s3]
    for i in message.text:
        if (i >= 'A') and (i <= 'Z'):
            i = (chr(ord(i) + 32))
        f = open('text.txt', 'r')
        for line in f:
            if line.rstrip('\n') == i:
                for j in range(N):
                    line1 = f.readline()
                    s[j] = s[j] + line1.rstrip('\n')
        f.close()

    bot.send_message(message.chat.id, "<pre>" + s[0] + "\n" + s[1] + "\n" + s[2] + "\n" + s[3] + "</pre>",
                     parse_mode=ParseMode.HTML)
    bot.send_message(message.chat.id, "Input the next word or type 0 to exit:")
    bot.register_next_step_handler(message, perevod)


def weather(message):
    s_city = message.text
    if s_city == '0':
        welcome(message)
        return
    city_id = 0
    appid = "c5d92db005513f33d2083e2e706ab3b5"
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': appid})
        data = res.json()
        cities = ["{} ({})".format(d['name'], d['sys']['country'])
                  for d in data['list']]
        city_id = data['list'][0]['id']
    except Exception as e:
        bot.send_message(message.chat.id, "нет такого города")
        bot.send_message(message.chat.id, "Input the next city:")
        bot.register_next_step_handler(message, weather)
        return

    try:
        #bot.send_message(message.chat.id, "city:" + str(cities))
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        bot.send_message(message.chat.id, "Погодные условия:" + data['weather'][0]['description'])
        bot.send_message(message.chat.id, "Температура:" + str(data['main']['temp']))
    except Exception as e:
        pass
    bot.send_message(message.chat.id, "Input the next city:")
    bot.register_next_step_handler(message, weather)


def calcul(message):
    a = []  # числа
    b = []  # знаки
    if not ((message.text[0] >= '0') and (message.text[0] <= '9') or message.text[0] == '(' or message.text[0] == '-'):
        welcome(message)
        return
    d = {'(': 0, ')': 0, '+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    c = message.text
    minus = False
    if (c[0] == '-'):
        minus = True
        c = c.replace('-', '', 1)

    temp = ''
    skob = 1
    for i in c:
        if i == '(':
            skob = 0
        elif i == ')':
            skob = 1
        if (i >= '0') and (i <= '9'):
            temp = temp + i
        else:
            if (temp != ''):
                a.append(temp)
                temp = ''
            bolly = True
            while (bolly):
                if (len(b) == 0) or (i == '(') or (d[b[len(b) - 1]] < d[i]):

                    if minus and i == '-' and skob:
                        b.append('+')
                    elif minus and i == '+' and skob:
                        b.append('-')
                    else:
                        b.append(i)
                    bolly = False
                else:
                    t = b.pop()
                    if t == '(' and i == ')':
                        break
                    x2 = a.pop()
                    x1 = a.pop()
                    if t == '+':
                        a.append(float(x1) + float(x2))
                    elif t == '-':
                        a.append(float(x1) - float(x2))
                    elif t == '*':
                        a.append(float(x1) * float(x2))
                    elif t == '/':
                        a.append(float(x1) / float(x2))

    if (temp != ''):
        a.append(temp)
    while (b != []):
        x2 = a.pop()
        x1 = a.pop()
        t = b.pop()
        if t == '+':
            a.append(float(x1) + float(x2))
        elif t == '-':
            a.append(float(x1) - float(x2))
        elif t == '*':
            a.append(float(x1) * float(x2))
        elif t == '/':
            a.append(float(x1) / float(x2))

    if minus == True:
        bot.send_message(message.chat.id, '-' + str(a[0]))
    else:
        bot.send_message(message.chat.id, a[0])

    a.clear()
    b.clear()
    bot.send_message(message.chat.id, "Input the next task:")
    bot.register_next_step_handler(message, calcul)


bot.polling(none_stop=True, interval=0)
