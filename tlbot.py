from TOKEN import TOKEN
from aiogram import Bot, Dispatcher, types, F, Router, BaseMiddleware
from aiogram.methods import SendMessage
from aiogram.filters import CommandStart
import asyncio
import sympy as sp
import re
from sympy import Eq, solve, symbols, parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication, convert_xor
import json
import aiosqlite
import matplotlib

from middlwares import Inject_language

matplotlib.use('Agg')  # Используем неинтерактивный бэкенд для matplotlib
import matplotlib.pyplot as plt
import io
import numpy as np
import middlewares
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

#texts = load_texts()

# Кастомные трансформации для парсера
transformations = (
    standard_transformations + (implicit_multiplication, convert_xor))

bot = Bot(token=TOKEN)#создаем экземпляр бота
dp = Dispatcher()
router = Router()
dp.include_router(router)
#Создаем БД
async def init_db():
    async with aiosqlite.connect('bot_data.db') as conn:
        # Создаем таблицу пользователей
        await conn.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     language TEXT DEFAULT 'RU',
                     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                     user_states INTEGER DEFAULT 0)''')
        await conn.commit()

#Для записи пользователя в БД
async def init_user(user_id: int) -> bool:
    """
    Добавляем нового пользователя в БД при первом запуске.
    Возвращает True, если пользователь создан, False если уже существует.
    """
    async with aiosqlite.connect('bot_data.db') as conn:
        cursor = await conn.cursor()
        # Проверяем, есть ли пользователь
        await cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        if await cursor.fetchone():
            return False  # Пользователь уже есть

        # Создаём нового
        await cursor.execute('''
        INSERT INTO users (user_id)
        VALUES (?)
        ''', (user_id,))
        await conn.commit()
        cursor.close()
        return True

async def update_user_language(user_id: int, language: str) -> bool:
    """
    Обновляет язык пользователя.
    Возвращает True при успехе, False если пользователя нет или возникновении ошибки
    """
    try:
        with sqlite3.connect('bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE users 
            SET language = ? 
            WHERE user_id = ?
            ''', (language, user_id))
            return cursor.rowcount > 0  # Были ли обновлены строки? da/net
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def update_user_state(user_id: int, state: str) -> bool:
    """
    Обновляет состояние пользователя .
    Возвращает True при успехе, False если пользователя нет или возникновении ошибки.
    """
    try:
        with sqlite3.connect('bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE users 
            SET user_states = ? 
            WHERE user_id = ?
            ''', (state, user_id))
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def get_user_language(user_id: int) -> str: #take language value
    with sqlite3.connect('bot_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0]  # возвращаем язык

def get_user_state(user_id: int) -> str: #take state value
    with sqlite3.connect('bot_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_states FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0]  # return state value

# Вызываем при старте бота

# BUTTONS
#REPLY_BTs


#INLINE_BTs
#language buttons
russian_lan_bt = types.InlineKeyboardButton(text='Русский🇷🇺', callback_data='RU')
english_lan_bt = types.InlineKeyboardButton(text='English🇬🇧', callback_data = 'EN')


# KEY BOARDS
#REPLY_KBs
"""
kb_info = {
    'RU': types.ReplyKeyboardMarkup(resize_keyboard=True).add(texts['RU']['skills'], texts['RU']['note']).row(texts['RU']['plot']),
    'EN': types.ReplyKeyboardMarkup(resize_keyboard=True).add(texts['EN']['skills'], texts['EN']['note']).row(texts['EN']['plot'])
}
"""
#INLINE_KBs
kb_language = types.InlineKeyboardMarkup(inline_keyboard = [[russian_lan_bt, english_lan_bt]])
 
# Функция для замены синусов и т.п
def zamena(x):
    # Заменяем знак степени
    x = re.sub(r'(sin|cos|tan|cot)\((\d+)\)', r'\1(math.radians(\2))', x)
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

def safe_parse_to_numpy(expr: str):
    # Приведение к нижнему регистру и удаление пробелов
    cleaned = expr.lower().replace(' ', '')

    # Заменяем сокращения и символы
    replacements = {
        'ctan': 'cot',
        'tg': 'tan',
        'cotan': 'cot',
        'cosec': 'csc',
        'secant': 'sec',
        '²': '**2',
        '³': '**3',
        '^': '**'
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    # Базовая защита от опасных ключевых слов
    if re.search(r'(__|import|lambda|eval|exec|system)', cleaned):
        raise ValueError("Недопустимые операции в выражении")
    # Парсинг выражения через SymPy
    try:
        parsed = parse_expr(cleaned, transformations=transformations, evaluate=False)
    except Exception as e:
        if "cannot be used as a variable" in str(e):
            raise ValueError("Недопустимое имя функции или переменной")
        elif "invalid syntax" in str(e):
            raise ValueError("Синтаксическая ошибка в выражении")
        else:
            raise ValueError(f"Ошибка парсинга: {str(e)}")

    # Проверка допустимых переменных
    allowed_symbols = {'x', 'e', 'pi'}
    used_symbols = {s.name for s in parsed.free_symbols}
    invalid = used_symbols - allowed_symbols
    if invalid:
        raise ValueError(f"Недопустимые переменные: {', '.join(invalid)}")

    # Замена e и pi на числовые значения
    parsed = parsed.subs({'e': sp.E, 'pi': sp.pi})

    # Преобразуем SymPy выражение в NumPy-совместимую функцию
    try:
        f_numpy = sp.lambdify("x", parsed, modules=["numpy"])
    except Exception:
        raise ValueError("Невозможно преобразовать выражение в NumPy функцию")

    return f_numpy

x_range = (-10,10)
def process_plot(message):
    chat_id = message.chat.id
    try:
        # Проверяем состояние ожидания ввода функции
        if get_user_state(chat_id) != 'waiting_function':
            match message.user_language:
                case "EN":
                    return bot.send_message(chat_id, text=f"Error")
                case "RU":
                    return bot.send_message(chat_id, text=f"Ошибка")

        text = message.text.strip()
        original_text = text
        x_range = (-10, 10)

        # Парсим выражение в безопасную NumPy-функцию
        f_numpy = safe_parse_to_numpy(text)

        # Генерируем график
        plot_buf = generate_plot(message, f_numpy, original_text, x_range)

        # Отправляем результат
        match message.user_language:
            case "EN":
                caption_template = texts['EN']['plot_caption']
                caption_filled = caption_template.format(
                    original_text=original_text,
                    x_min=x_range[0],
                    x_max=x_range[1]
                )
                bot.send_photo(chat_id, plot_buf, caption=caption_filled, parse_mode='HTML')
            case "RU":
                caption_template = texts['RU']['plot_caption']
                caption_filled = caption_template.format(
                    original_text=original_text,
                    x_min=x_range[0],
                    x_max=x_range[1]
                )
                bot.send_photo(chat_id, plot_buf, caption=caption_filled, parse_mode='HTML')
    except Exception as e:
        # Обработка сообщений об ошибках
        error_msg = str(e)
        match message.user_language:
            case "EN":
                bot.send_message(chat_id, text=f"Error: {error_msg}")
            case "RU":
                bot.send_message(chat_id, text=f"Ошибка: {error_msg}")
        print(e)
        # Запрашиваем ввод заново
        match message.user_language:
            case "EN":
                msg = bot.send_message(chat_id, text=texts["EN"][f"plot_try_again"])
            case "RU":
                msg = bot.send_message(chat_id, text=texts["RU"][f"plot_try_again"])
        bot.register_next_step_handler(msg, process_plot)
        return
    finally:
        # Сбрасываем состояние пользователя
        update_user_state(chat_id, "nothing")


# Функция генерации графика

def generate_plot(message, f_numpy, expr_str: str, x_range: tuple = (-10, 10)) -> io.BytesIO:
    # Проверка корректности диапазона
    if x_range[1] <= x_range[0]:
        raise ValueError("Некорректный диапазон значений X")

    # Создаём массив точек
    x = np.linspace(x_range[0], x_range[1], 1000)

    # Вычисляем значения функции с подавлением предупреждений
    with np.errstate(all='ignore'):
        y = f_numpy(x)

    # Маскируем бесконечности и NaN
    y = np.ma.masked_invalid(y)
    y = np.ma.masked_where(np.abs(y) > 1e5, y)

    # Построение графика
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x, y, linewidth=2)

    # Настройка осей для тригонометрических функций
    if any(fn in expr_str.lower() for fn in ['sin', 'cos', 'tan', 'cot', 'csc', 'sec']):
        ax.set_ylim(-5, 5)
        ax.set_yticks(np.arange(-5, 6, 1))

    ax.grid(True, linestyle='--', alpha=0.7)
    match message.user_language:
        case "EN":
            ax.set_title(f'Plot: {expr_str}', fontsize=14)
        case "RU":
            ax.set_title(f'График: {expr_str}', fontsize=14)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.set_xlim(x_range)

    # Сохранение в буфер
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
# HAHDLERS
#middleware, для обработки сообщений и callbacks, после передавать в остальные
middleware = Inject_language(db_path="bot_data.db")
dp.message.middleware(middleware)

#choose language and start
@router.message(CommandStart())
@router.message(F.text.lower().in_(["привет", "начать", "hi"]))
async def start_reply(message: types.Message):
    await message.answer(text='Привет!👋\n'
                                           'Пожалуйста выбери язык, на котором тебе будет комфортно общаться:\n\n'
                                           'Hi👋\n'
                                           'Please choose a language:', reply_markup=kb_language)
    await init_user(message.from_user.id)
"""
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

#Решение уравнений
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
                bot.send_message(message.chat.id, text=f'{texts['RU']['error']}{e}')

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
                bot.send_message(message.chat.id, text=f'{texts['RU']['error']}{e}')

# Запрос на график
@bot.message_handler(commands=['plot', 'график'])
@bot.message_handler(func=lambda message: message.text in ['График📈', 'Plot📈'])
def start_plot(message):
    match message.user_language:
        case "EN":
            msg = bot.send_message(message.chat.id, text=texts['EN']['plot_message'], parse_mode='HTML')
        case "RU":
            msg = bot.send_message(message.chat.id, text=texts['RU']['plot_message'], parse_mode='HTML')
    update_user_state(message.from_user.id, 'waiting_function')
    bot.register_next_step_handler(msg, process_plot)

# Хендлер для остальных сообщений
@router.message()
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
                bot.send_message(message.chat.id, text=f'{texts['RU']['error']}{e}')
  """
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

