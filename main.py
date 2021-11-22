import telebot
from telebot import types
import sqlite3
import requests
import bs4

#token = '2063328479:AAHRBWbBKhrIm7uUx_lKtmip4TIMWDmflVg'
token = '2053227138:AAFUYTGgNmjCh9-Ah-7-_6sGSbke_hfIIK8'
bot = telebot.TeleBot(token)

connection = sqlite3.connect('users.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(userId INT PRIMARY KEY,team text);""")

connection.commit()




state = 0


def get_state():
    return state

def g_team(result):
    response = requests.get('https://www.sports.ru/' + result + '/calendar/')

    page = bs4.BeautifulSoup(response.content, 'html5lib')

    item = page.find('div', 'score score-orange')
    if item == None:
        item = page.find('div', 'score score-green')
    if item == None:
        item = page.find('div', 'score score-red')
    score = item.text
    m = []
    for i in range(len(score)):
        if score[i] != '\n':
            m.append(score[i])
    s = str(m[0]) + ':' + str(m[1])

    item = page.find('div', 'commands')

    cc = ''
    for i in range(len(item.text)):
        if item.text[i] != '\n':
            cc += item.text[i]
    g=[cc, s]
    a = ''
    for i in g:
        a += str(i) + '   '
    return  a

def chatid(message):
    local_connection = sqlite3.connect('users.db')
    local_cursor = local_connection.cursor()
    result = local_cursor.execute(f'SELECT team from users where userId = {message};').fetchone()[0]
    return result


@bot.message_handler(commands=['start'])
def get_team(message):
    bot.send_message(message.chat.id, 'Привет! Любишь футбол? Тогда ты по адресу! За какую команду болеешь?')
    global state
    state = 1

@bot.message_handler(commands=['start2'])
def get_team(message):
    bot.send_message(message.chat.id, 'Привет! Мы тебя ждали')
    global state
    state = 2


@bot.message_handler(func=lambda message: get_state() == 1)
def f_team(message):
    team = message.text
    try:
        local_connection = sqlite3.connect('users.db')
        local_cursor = local_connection.cursor()
        local_cursor.execute("INSERT INTO users VALUES(?, ?);", (message.chat.id, team))
        local_connection.commit()
    except Exception:
        bot.send_message(message.chat.id, "Мы уже знаем за какую команду ты болеешь")
    finally:
        global state
        state = 2

@bot.message_handler(func=lambda message: get_state() == 2)
def k_team(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton('Хочу', callback_data='g')
    markup.add(btn)
    bot.send_message(message.chat.id, "Хотите узнать счёт последнего матча?", reply_markup=markup)
    global state
    state = 3



@bot.callback_query_handler(func=lambda call:True)
def button(call):
    if call.message:
        if call.data == 'g':
            bot.send_message(call.message.chat.id, "Вы хотите посмотреть счёт команды, за которую болеете или другую? ")


@bot.message_handler(func=lambda message: get_state() == 3)
def f(message):
    choice = message.text
    global state
    if choice == 'За которую болею':
        state = 4
        bot.send_message(message.chat.id, "Как вы думаете сколько голов забила ваша любимая команда?")
    elif choice == 'Другую':
        state = 5
        bot.send_message(message.chat.id, "Введите название команды")



@bot.message_handler(func=lambda message: get_state() == 4)
def get_score1(message):
    try:
        result = chatid(message.chat.id)
        bot.send_message(message.chat.id, g_team(result))
        global state
        state = 2
    except Exception:
            bot.send_message(message.chat.id, "Такой команды нет. Попробуйте ещё раз")

@bot.message_handler(func=lambda message: get_state() == 5)
def get_score2(message):
    result = message.text
    try:
        bot.send_message(message.chat.id, g_team(result))
        global state
        state = 2
    except Exception:
            bot.send_message(message.chat.id, "Такой команды нет. Попробуйте ещё раз")




@bot.message_handler(commands=['get_subscribers'])
def get_subscribers(message):
    local_connection = sqlite3.connect('users.db')
    local_cursor = local_connection.cursor()
    local_cursor.execute("SELECT * from users;")
    all_results = local_cursor.fetchall()
    bot.send_message(message.chat.id, str(all_results))




bot.polling(none_stop=True, interval=0)

