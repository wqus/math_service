from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import CallbackQuery

from TOKEN import TOKEN
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
import redis.asyncio as redis

import sympy as sp
import re
from sympy import Eq, solve, symbols, parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication, convert_xor
import json
import aiosqlite
import aiofiles
import matplotlib

from middlwares import Inject_language

#matplotlib.use('Agg')  # Используем неинтерактивный бэкенд для matplotlib
import matplotlib.pyplot as plt
import io
import numpy as np

class PlotStates(StatesGroup):#класс состояний для графика
    waiting_for_function = State()

# 1. Загрузка текстовых ресурсов
async def load_texts():
    try:
        async with aiofiles.open('text_ru.json', 'r', encoding='utf-8') as f:
            ru_content = await f.read()
            texts_ru = json.loads(ru_content)
        async with aiofiles.open('text_en.json', 'r', encoding='utf-8') as f:
            en_content = await f.read()
            texts_en = json.loads(en_content)
        return {'RU': texts_ru, 'EN': texts_en}
    except FileNotFoundError as e:
        print(f"Ошибка загрузки файлов переводов: {e}")
        exit(1)

texts = asyncio.run(load_texts())
# Кастомные трансформации для парсера
transformations = (
    standard_transformations + (implicit_multiplication, convert_xor))

def on_startup(): #on startup
    global redis_client
    redis_c = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, max_connections=25,
                               health_check_interval=30, socket_timeout=4)
    #redis_c.ping()
    return redis_c
    #await init_db()
    #matplotlib.use('Agg')
redis_client = on_startup()
async def close_redis(): #on_shutdown
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
bot = Bot(token=TOKEN)#создаем экземпляр бота
dp = Dispatcher(storage = RedisStorage(redis = redis_client))
print(type(redis_client))
router = Router()

#middleware, для обработки сообщений и callbacks, после передавать в остальные
middleware = Inject_language(db_path="bot_data.db")
dp.message.middleware(middleware)
#add router
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
        async with aiosqlite.connect('bot_data.db') as conn:
            cursor = await conn.cursor()
            await cursor.execute('''
            UPDATE users 
            SET language = ? 
            WHERE user_id = ?
            ''', (language, str(user_id)))
            await conn.commit() #сохраняем изменения
            return cursor.rowcount > 0  # Были ли обновлены строки? da/net
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return False

async def update_user_state(user_id: int, state: str) -> bool:
    """
    Обновляет состояние пользователя .
    Возвращает True при успехе, False если пользователя нет или возникновении ошибки.
    """
    try:
        async with aiosqlite.connect('bot_data.db') as conn:
            cursor = await conn.cursor()
            await cursor.execute('''
            UPDATE users 
            SET user_states = ? 
            WHERE user_id = ?
            ''', (state, user_id))
            await conn.commit() #сохраняем изменения
            return await cursor.rowcount > 0
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return False

async def get_user_state(user_id: int) -> str: #take state value
    async with aiosqlite.connect('bot_data.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute('SELECT user_states FROM users WHERE user_id = ?', (user_id,))
        result = await cursor.fetchone()
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
kb_info = {
    'RU': types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text = texts['RU']['skills']), types.KeyboardButton(text = texts['RU']['note'])], [types.KeyboardButton(text = texts['RU']['plot'])]],resize_keyboard=True),
    'EN': types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text = texts['EN']['skills']), types.KeyboardButton(text = texts['EN']['note'])], [types.KeyboardButton(text = texts['EN']['plot'])]],resize_keyboard=True)
}

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
def safe_parse_to_numpy_answer(expr: str):
    def replaces(match):
        #фукция для замены градусов в триганометрических функциях на радианы, вызывается автоматически в re.sub при нахожденнии совпадений
        func_name = match.group(1)
        degrees_to_radians = np.radians(int(match.group(2)))
        return f"{func_name}({degrees_to_radians})"
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
    cleaned = re.sub(r'(sin|cos|tan|cot)\((\d+)\)',replaces, cleaned)
    # Парсинг выражения через SymPy
    try:
        parsed = parse_expr(cleaned, transformations=transformations)
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
    return parsed

def safe_parse_to_numpy_function(expr: str):
    def replaces(match):
        #фукция для замены градусов в триганометрических функциях на радианы, вызывается автоматически в re.sub при нахожденнии совпадений
        func_name = match.group(1)
        degrees_to_radians = np.radians(int(match.group(2)))
        return f"{func_name}({degrees_to_radians})"
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
    cleaned = re.sub(r'(sin|cos|tan|cot)\((\d+)\)',replaces, cleaned)
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

# Функция генерации графика
def generate_plot(f_numpy, expr_str: str, user_language: str) -> io.BytesIO:
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
    ax.set_xticks(np.arange(-10, 11, 1))
    # Настройка осей для тригонометрических функций
    if any(fn in expr_str.lower() for fn in ['sin', 'cos', 'tan', 'cot', 'csc', 'sec']):
        ax.set_ylim(-5, 5)
        ax.set_yticks(np.arange(-5, 6, 1))

    ax.grid(True, linestyle='--', alpha=0.7)
    match user_language:
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
#choose language and start
@router.message(CommandStart())
@router.message(F.text.lower().in_(["привет", "начать", "hi"]))
async def start_reply(message: types.Message):
    await message.answer(text='Привет!👋\n'
                                           'Пожалуйста выбери язык, на котором тебе будет комфортно общаться:\n\n'
                                           'Hi👋\n'
                                           'Please choose a language:', reply_markup=kb_language)
    await init_user(message.from_user.id)

#HI message, 2 languages
language_array = ['RU', 'EN']
@router.callback_query()
async def call_handler(callback: CallbackQuery):
    match callback:
        case _ if callback.data in language_array:
            await callback.answer()
            await callback.message.answer(text=f"{texts[callback.data]['start']}", reply_markup=kb_info[callback.data])
            await update_user_language(callback.from_user.id, callback.data)
# ответ на умения
@router.message(Command(commands=["skills", "умения"]))
@router.message(F.text.in_([texts['RU']['skills'], "умения", texts['EN']['skills'], "skills"]))
@router.message(F.text.lower().in_(["умения", "skills", "возможности", "способности"]))
async def skills(message: types.Message, user_language: str):
    match user_language:
        case "EN":
            await message.answer(text= texts['EN']['skills_answer'])
        case "RU":
            await message.answer(text=texts['RU']['skills_answer'])

# ответ на примечание
@router.message(Command(commands=["rules", "примечание"]))
@router.message(F.text.in_([texts['RU']['note'], texts['EN']['note']]))
@router.message(F.text.lower().in_(["примечание", "rules", "правила", "note"]))
async def primec(message: types.Message, user_language: str):
    match user_language:
        case "EN":
            await message.answer(text= texts['EN']['note_answer'], parse_mode='HTML')
        case "RU":
            await message.answer(text=texts['RU']['note_answer'], parse_mode='HTML')

# Хендлер для неравенств
@router.message(lambda message: any(s in message.text for s in ['<','<=','>=','>']))
async def solve_inequality(message: types.Message, user_language: str):
    try:
        user_input = message.text.lower()

        # Заменяем символы для представления бесконечности
        user_input = user_input.replace('oo', 'sp.oo')

        # Решаем неравенство
        x = sp.symbols('x')
        solution = sp.solve_univariate_inequality(safe_parse_to_numpy_answer(user_input), x, relational=False)

        #в красивую строку
        formatted_solution = sp.pretty(solution, use_unicode=True)
        await message.answer(text=f'x ∈ {formatted_solution}')

    except Exception as e: #выводим в сообщение об ошибке
        match user_language:
            case "EN":
                await message.answer(text=f'{texts['EN']['error']}{e}')
            case "RU":
                await message.answer(text=f'{texts['RU']['error']}{e}')

#Решение уравнений
@router.message(F.text.contains("="))
async def solve_equation_or_expression(message: types.Message, user_language: str):
    try:
        # Вводим переменную
        x = symbols('x')

        # Преобразовываем уравнение
        user_input = message.text

        # Разделяем уравнение на левую и правую части
        equation_parts = user_input.split('=')

        # Решаем уравнение и выводим ответ пользователю
        if len(equation_parts) == 2:
            left = equation_parts[0]
            right = equation_parts[1]

            equation = Eq(safe_parse_to_numpy_answer(left), safe_parse_to_numpy_answer(right))

            # Решаем уравнение
            result = solve(equation, x)

            formatted_res = ('; '.join(
                [f'x = {str(round(sol, 3)).rstrip("0").rstrip(".") if "." in str(sol) else str(sol)}' for sol in
                 result]))
            match user_language: #отправляем ответ
                case "EN":
                    await message.answer(text=formatted_res)
                case "RU":
                    await message.answer(text=formatted_res)
        else: #иначе сообщаем о некорректном вводе
            match user_language:
                case "EN":
                    await message.answer(text=texts['EN']['wrong_input'])
                case "RU":
                    await message.answer(text=texts['RU']['wrong_input'])

    except Exception as e: #выводим в сообщение об ошибке
        match user_language:
            case "EN":
                await message.answer(text=f'{texts['EN']['error']}{e}')
            case "RU":
                await message.answer(text=f'{texts['RU']['error']}{e}')

# Запрос на график
@router.message(Command(commands=["plot", "график"]))
@router.message(F.text.lower().in_(["график📈", "график", "plot📈", "plot"]))
async def start_plot(message: types.Message, user_language: str, state: FSMContext):
    match user_language:
        case "EN":
            await message.answer(text=texts['EN']['plot_message'], parse_mode='HTML')
        case "RU":
            await message.answer(text=texts['RU']['plot_message'], parse_mode='HTML')
    await state.set_state(PlotStates.waiting_for_function)

x_range = (-10,10)
#Хендлер обработки запросов по состоянию PlotStates.waiting_for_function
@router.message(PlotStates.waiting_for_function)
async def process_plot(message: types.Message, state: FSMContext, user_language: str):
    try:
        text = message.text.strip()
        original_text = text

        # Парсим выражение в безопасную NumPy-функцию
        f_numpy = safe_parse_to_numpy_function(text)
        # Генерируем график
        plot_buf = generate_plot(f_numpy, original_text, user_language)
        raw_bytes = plot_buf.read()
        photo_file = types.BufferedInputFile(raw_bytes, "plot.png")
        # Отправляем результат
        match user_language:
            case "EN":
                caption_template = texts['EN']['plot_caption']
                caption_filled = caption_template.format(
                    original_text=original_text,
                    x_min=x_range[0],
                    x_max=x_range[1]
                )
                await message.answer_photo(photo = photo_file, caption=caption_filled, parse_mode='HTML')
            case "RU":
                caption_template = texts['RU']['plot_caption']
                caption_filled = caption_template.format(
                    original_text=original_text,
                    x_min=x_range[0],
                    x_max=x_range[1]
                )
                await message.answer_photo(photo = photo_file, caption=caption_filled, parse_mode='HTML')
        await state.clear()
        return None
    except Exception as e:
        # Обработка сообщений об ошибках и запрос на повторный ввод
        error_msg = str(e)
        match user_language:
            case "EN":
                await message.answer(text=f"Error: {error_msg}")
                await message.answer(text=texts["EN"][f"plot_try_again"])
            case "RU":
                await message.answer(text=f"Ошибка: {error_msg}")
                await message.answer(text=texts["RU"][f"plot_try_again"])
        print(e)
        return None

# Хендлер для остальных сообщений
@router.message()
async def handle_expression(message: types.Message, user_language: str):
    try:
        # Преобразовываем выражение
        user_input = message.text.lower()

        # Решаем выражение
        answer = safe_parse_to_numpy_answer(user_input)

        formatted_res = str(round(answer, 3)).rstrip('0').rstrip('.') if '.' in str(answer) else str(answer)
        match user_language:  # отправляем ответ
            case "EN":
                await message.answer(text=formatted_res)
            case "RU":
                await message.answer(text=formatted_res)

    except Exception as e:
        match user_language:
            case "EN":
                await message.answer(text=f'{texts['EN']['error']}{e}')
            case "RU":
                await message.answer(text=f'{texts['RU']['error']}{e}')

async def main(): #функция при запуске
    await dp.start_polling(bot)
    await init_db()
    matplotlib.use('Agg')
    dp.shutdown.register(close_redis)

if __name__ == "__main__":
    asyncio.run(main())
