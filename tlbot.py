from TOKEN import TOKEN
import telebot
from telebot import types
import sympy as sp
import math
import re
from sympy import Eq, solve, symbols, parse_expr, sin, cos, tan, cot, rad
import json

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
bot = telebot.TeleBot(token=TOKEN)

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
#choose language and start
@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text.lower() in ['начать', 'привет'])
def start_reply(message):
    if
    bot.send_message(message.chat.id, text='Привет!👋\n'
                                           'Пожалуйста выбери язык, на котором тебе будет комфортно общаться:\n\n'
                                           'Hi👋\n'
                                           'Please choose a language:', reply_markup=kb_language)
#HI message, 2 languages
@bot.callback_query_handler(func=lambda call: True)  
def call_handler(call):
    user_language = call.data
    match call.data:  
        case 'RU':  
            bot.send_message(call.message.chat.id, "Привет!👋\n\nЯ твой помощник по математике!📊\nНапиши мне свою задачу и я постораюсь её решить!", reply_markup= kb_info[user_language])
        case 'EN':
            bot.send_message(call.message.chat.id, "Hi!👋\n\nI'm your math assistant!📊\nWrite me your problem and I'll try to solve it!", reply_markup= kb_info[user_language])

# ответ на умения
@bot.message_handler(commands=['skills'])
@bot.message_handler(func=lambda message: message.text in ['Умения🤓'])
def skills(message):
    bot.send_message(message.chat.id, text='Вот все, что я умею решать 📝:\n\n'
                                           '1. Примеры\n'
                                           '2. Уравнения с одной переменной\n'
                                           '3. Неравенства\n\n'
                                           'Также ведется активная разработка и множества другого!🧑🏻‍💻')


# ответ на примечание
@bot.message_handler(commands=['rules'])
@bot.message_handler(func=lambda message: message.text in 'Примечание📃')
def primec(message):
    bot.send_message(message.chat.id, text='<b>Примечание📃</b>:\n\n'
                                           '   <b>1. Для умножения используется знак "*"</b>\n'
                                           'Примеры записи:\n'
                                           '        5x❌\n'
                                           '        5 * x✅\n'
                                           '        4 * 3✅\n\n'

                                           '   <b>2. Для записи степени используется "**" или "^"</b>\n'
                                           'Примеры записи:\n'
                                           '       2^4 (2 в 4-ой степени)\n '
                                           '      x ** 2 (x во 2-ой степени)\n\n'

                                           '   <b>3.При записи уравнений использовать "x"</b>\n'
                                           'Примеры записи:\n'
                                           '       5 * a = 10❌\n'
                                           '       5 * x = 10✅\n\n'

                                           '   <b>4. Градусы для sin, cos, tg, ctg записываются в скобках"</b>\n'
                                           'Примеры записи:\n'
                                           '       cos 15 ❌\n'
                                           '       sin(30)✅\n'
                                           '       sin(45) + tg(90)✅\n\n'
                                           '<b>Если бот отправил пустой ответ - это означает, что пример нерешаем</b>', parse_mode='HTML')


@bot.message_handler(commands=['info'])
@bot.message_handler(func=lambda message: message.text in ['Информация🥸'])
def info(message):
    bot.send_message(message.chat.id, text=
    'В будущем будет мощный текст или ваще другая кнопка, просто их мало, а для красоты надо хотя бы 3 иметь💪🏻😈')


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
            bot.send_message(message.chat.id, text=f'Ответ: {formatted_res}')

        else:
            bot.send_message(message.chat.id,
                             text='Некорректное уравнение.\n\n Проверь свою запись и попробуй еще раз!')

    except Exception as e:
        bot.send_message(message.chat.id,
                         text=f'Произошла ошибка:(\n\nОшибка(для разработчика, в будущем этого не будет): {e} ')


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

        bot.send_message(message.chat.id, text='Ответ: x ∈ ' + formatted_solution)

    except Exception as e:
        bot.send_message(message.chat.id, text=f'Произошла ошибка\n\n{e}(для разраба)')


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
        bot.send_message(message.chat.id, text=f'Ответ: {formatted_res}')

    except Exception as e:
        bot.send_message(message.chat.id,
                         text=f'Произошла ошибка:(\n\n\Ошибка(для разработчика, в будущем этого не будет): {e} ')
bot.polling()
