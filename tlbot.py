from TOKEN import TOKEN
import telebot
from telebot import types, apihelper
import sympy as sp
import math
import re
from sympy import Eq, solve, symbols, parse_expr, sin, cos, tan, cot, rad
import json
import sqlite3


# 1. Загрузка текстовых ресурсов
def load_texts():
    try:
        with open('text_ru.json', 'r', encoding='utf-8') as f:
            texts_ru = json.load(f)
        with open('text_en.json', 'r', encoding='utf-8') as f:
            texts_en = json.load(f)
        return {'RU': texts_ru, 'EN': texts_en}
    except FileNotFoundError as e:
        print(f"Ошибка загрузки файлов переводов: {e}")
        exit(1)

texts = load_texts()
# Включаем поддержку middleware
apihelper.ENABLE_MIDDLEWARE = True

bot = telebot.TeleBot(token=TOKEN)#создаем экземпляр бота

#Создаем БД
def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()

    # Создаем таблицу пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 language TEXT DEFAULT 'RU',
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()


#Для записи пользователя в БД
def init_user(user_id: int) -> bool:
    """
    Добавляем нового пользователя в БД при первом запуске.
    Возвращает True, если пользователь создан, False если уже существует.
    """
    with sqlite3.connect('bot_data.db') as conn:
        cursor = conn.cursor()
        # Проверяем, есть ли пользователь
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            return False  # Пользователь уже есть

        # Создаём нового
        cursor.execute('''
        INSERT INTO users (user_id)
        VALUES (?)
        ''', (user_id,))
        return True

def update_user_language(user_id: int, language: str) -> bool:
    """
    Обновляет язык пользователя.
    Возвращает True при успехе, False если пользователя нет.
    """
    with sqlite3.connect('bot_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE users 
        SET language = ? 
        WHERE user_id = ?
        ''', (language, user_id))
        return cursor.rowcount > 0  # Были ли обновлены строки? da/net

def get_user_language(user_id: int) -> str: #take language value
    with sqlite3.connect('bot_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0]  # возвращаем язык

# Вызываем при старте бота
init_db()

# BUTTONS
#REPLY_BTs


#INLINE_BTs
#language buttons
russian_lan_bt = types.InlineKeyboardButton(text='Русский🇷🇺', callback_data='RU')
english_lan_bt = types.InlineKeyboardButton(text='English🇬🇧', callback_data = 'EN')


# KEY BOARDS
#REPLY_KBs
kb_info = {
    'RU': types.ReplyKeyboardMarkup(resize_keyboard=True).add(texts['RU']['skills'], texts['RU']['note']).row(texts['RU']['information']),
    'EN': types.ReplyKeyboardMarkup(resize_keyboard=True).add(texts['EN']['skills'], texts['EN']['note']).row(texts['EN']['information'])
}

#INLINE_KBs
kb_language = types.InlineKeyboardMarkup(row_width=2)
kb_language.add(russian_lan_bt, english_lan_bt)
 
# Функция для замены синусов и т.п
def zamena(x):
    # Заменяем знак степени
    x = re.sub(r'(\d+)\)', r'math.radians(\1))', x)
    # Заменяем тригонометрические функции
    x = x.replace('sin(', 'math.sin(')
    x = x.replace('cos(', 'math.cos(')
    x = x.replace('tan(', 'math.tan(')
    return x


# Функция для обработки знака = в неравенствах
def solve_inequality(user_input: str, inequality_type: str):
    # Заменяем символы для представления бесконечности
    user_input = user_input.replace('oo', 'sp.oo')

    # Разделяем неравенство на левую и правую части
    left, right = user_input.split(inequality_type)
    left_expr = sp.parse_expr(left)
    right_expr = sp.parse_expr(right)

    # Решаем неравенство
    solution = sp.solve_univariate_inequality(sp.Eq(left_expr, right_expr), sp.symbols('x'), relational=False)

    # Преобразуем решение в красивую строку
    formatted_solution = sp.pretty(solution, use_unicode=True)
    return formatted_solution

# HAHDLERS
#middleware, для обработки сообщений и callbacks, после передавать в остальные
@bot.middleware_handler(update_types=['message', 'callback_query'])
def inject_language(bot_instance, update):
    try:
        if hasattr(update, 'from_user'):
            update.user_language = get_user_language(update.from_user.id)
    except Exception as e:
        print(f"Language error: {e}")
        update.user_language = 'RU'

#choose language and start
@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text.lower() in ['начать', 'привет', 'hi'])
def start_reply(message):
    bot.send_message(message.chat.id, text='Привет!👋\n'
                                           'Пожалуйста выбери язык, на котором тебе будет комфортно общаться:\n\n'
                                           'Hi👋\n'
                                           'Please choose a language:', reply_markup=kb_language)
    init_user(message.from_user.id)

#HI message, 2 languages
@bot.callback_query_handler(func=lambda call: True)  
def call_handler(call):
    user_language = call.data
    match call.data:
        case 'RU':
            bot.send_message(call.message.chat.id, text=f"{texts['RU']['start']}", reply_markup=kb_info[user_language])
        case 'EN':
            bot.send_message(call.message.chat.id, text=f"{texts['EN']['start']}", reply_markup=kb_info[user_language])
    update_user_language(call.from_user.id, call.data)

# ответ на умения
@bot.message_handler(commands=['skills'])
@bot.message_handler(func=lambda message:  message.text in [texts['RU']['skills'], texts['EN']['skills']])
def skills(message):
    match message.user_language:
        case "EN":
            bot.send_message(message.chat.id, text= texts['EN']['skills_answer'])
        case "RU":
            bot.send_message(message.chat.id, text=texts['RU']['skills_answer'])

# ответ на примечание
@bot.message_handler(commands=['rules'])
@bot.message_handler(func=lambda message: message.text in [texts['RU']['note'], texts['EN']['note']])
def primec(message):
    match message.user_language:
        case "EN":
            bot.send_message(message.chat.id, text= texts['EN']['note_answer'], parse_mode='HTML')
        case "RU":
            bot.send_message(message.chat.id, text=texts['RU']['note_answer'], parse_mode='HTML')

@bot.message_handler(commands=['info'])
@bot.message_handler(func=lambda message: message.text in [texts['RU']['information'], texts['EN']['information']])
def info(message):
    match message.user_language:
        case "EN":
            bot.send_message(message.chat.id, text= texts['EN']['information_answer'], parse_mode='HTML')
        case "RU":
            bot.send_message(message.chat.id, text=texts['RU']['information_answer'], parse_mode='HTML')

@bot.message_handler(func=lambda message: '=' in message.text)
def solve_equation_or_expression(message):
    try:
        # Вводим переменную
        x = symbols('x')

        # Преобразовываем уравнение

        user_input = message.text.lower()
        user_input = user_input.replace('^', '**')
        user_input = zamena(user_input)

        # Разделяем уравнение на левую и правую части
        equation_parts = user_input.split('=')

        # Решаем уравнение и выводим ответ пользователю
        if len(equation_parts) == 2:
            left = equation_parts[0]
            right = equation_parts[1]

            equation = Eq(eval(left), eval(right))

            # Решаем уравнение
            result = solve(equation, x)

            formatted_res = ('; '.join(
                [f'x = {str(round(sol, 3)).rstrip("0").rstrip(".") if "." in str(sol) else str(sol)}' for sol in
                 result]))
            match message.user_language: #отправляем ответ
                case "EN":
                    bot.send_message(message.chat.id, text=formatted_res)
                case "RU":
                    bot.send_message(message.chat.id, text=formatted_res)
        else: #иначе сообщаем о некорректном вводе
            match message.user_language:
                case "EN":
                    bot.send_message(message.chat.id, text=texts['EN']['wrong_input'])
                case "RU":
                    bot.send_message(message.chat.id, text=texts['RU']['wrong_input'])

    except Exception as e: #выводим в сообщение об ошибке
        match message.user_language:
            case "EN":
                bot.send_message(message.chat.id, text=f'{texts['EN']['error']}{e}')
            case "RU":
                bot.send_message(message.chat.id, text=f'{texts['EN']['error']}{e}')

# Хендлер для неравенств
@bot.message_handler(func=lambda message: '<' in message.text or '>' in message.text or '>=' in message.text or '<=' in message.text)
def solve_inequality(message: types.Message):
    try:
        user_input = message.text.lower()

        # Заменяем символы для представления бесконечности
        user_input = user_input.replace('oo', 'sp.oo')

        # Решаем неравенство
        x = sp.symbols('x')
        solution = sp.solve_univariate_inequality(sp.parse_expr(user_input), x, relational=False)

        #в красивую строку
        formatted_solution = sp.pretty(solution, use_unicode=True)
        bot.send_message(message.chat.id, text=f'x ∈ {formatted_solution}')

    except Exception as e: #выводим в сообщение об ошибке
        match message.user_language:
            case "EN":
                bot.send_message(message.chat.id, text=f'{texts['EN']['error']}{e}')
            case "RU":
                bot.send_message(message.chat.id, text=f'{texts['EN']['error']}{e}')

# Хендлер для остальных сообщений
@bot.message_handler()
def handle_expression(message: types.Message):
    try:
        # Преобразовываем выражение
        user_input = message.text.lower()
        user_input = zamena(user_input)

        # Решаем выражение
        result = eval(user_input)

        formatted_res = str(round(result, 3)).rstrip('0').rstrip('.') if '.' in str(result) else str(result)
        match message.user_language:  # отправляем ответ
            case "EN":
                bot.send_message(message.chat.id, text=formatted_res)
            case "RU":
                bot.send_message(message.chat.id, text=formatted_res)

    except Exception as e:
        match message.user_language:
            case "EN":
                bot.send_message(message.chat.id, text=f'{texts['EN']['error']}{e}')
            case "RU":
                bot.send_message(message.chat.id, text=f'{texts['EN']['error']}{e}')
bot.polling()
