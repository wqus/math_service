import re
import sympy as sp
import numpy as np
import io
import matplotlib.pyplot as plt
from sympy import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication, convert_xor
from db.engine import engine
from sqlalchemy import text
from datetime import datetime
from keyboards.inline_kbs import answer_to_ticket_kb, load_three_tickets_kb, unban_user_kb
from repositories.support_messages_repository import take_tickets_for_support, take_bans

transformations = (
        standard_transformations + (implicit_multiplication, convert_xor))


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
        # фукция для замены градусов в триганометрических функциях на радианы, вызывается автоматически в re.sub при нахожденнии совпадений
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
    cleaned = re.sub(r'(sin|cos|tan|cot)\((\d+)\)', replaces, cleaned)
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
        # фукция для замены градусов в триганометрических функциях на радианы, вызывается автоматически в re.sub при нахожденнии совпадений
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
    cleaned = re.sub(r'(sin|cos|tan|cot)\((\d+)\)', replaces, cleaned)
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


x_range = (-10, 10)


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


async def save_user_message(user_id, input_message, output_message):
    async with engine.begin() as conn:
        await conn.execute(
            text('''INSERT INTO history(user_id, input_message, output_message)
                     VALUES (:user_id, :input_message, :output_message)'''),
            {"user_id": user_id, "input_message": input_message, "output_message": output_message}
        )


async def requests_history(user_id, cursor=None, page_size=10, direction="next"):
    query = "SELECT id, input_message, output_message, created_at FROM history WHERE user_id = :user_id"
    params = {"user_id": user_id}

    # курсорная навигация
    if cursor:
        cursor_id, cursor_created_at = cursor
        params["created_at"] = cursor_created_at
        params["id"] = cursor_id
        print(f"CURSOR: {cursor}")
        if direction == "next":
            query += " AND (created_at < :created_at OR (created_at = :created_at AND id < :id))"
        elif direction == "prev":
            query += " AND (created_at > :created_at OR (created_at = :created_at AND id > :id))"

    if direction == "prev":
        query += f" ORDER BY created_at, id LIMIT {page_size}"
    else:
        query += f" ORDER BY created_at DESC, id DESC LIMIT {page_size}"

    async with engine.connect() as conn:
        result = await conn.execute(
            text(query), params)

    prev_cursor, next_cursor = None, None

    rows = result.fetchall()
    print(rows)
    if rows:
        if direction == "prev":
            rows.reverse()  # чтобы вернуть естественный порядок
        first = rows[0]
        last = rows[-1]
        async with engine.connect() as conn:
            newer = await conn.execute(text(
                """
                SELECT 1 FROM history
                WHERE user_id = :user_id AND (created_at > :created_at OR (created_at = :created_at AND id > :id))
                LIMIT 1
                """), {'user_id': user_id, 'created_at': first[3], 'id': first[0]})
            if newer.first():
                prev_cursor = (first[0], first[3])
            # проверяем наличие записей старее (для next-кнопки)
            older = await conn.execute(text(
                """
                SELECT 1 FROM history
                WHERE user_id = :user_id
                AND (created_at < :created_at OR (created_at = :created_at AND id < :id))
                LIMIT 1
                """), {'user_id': user_id, 'created_at': last[3], 'id': last[0]})
            if older.first():
                next_cursor = (last[0], last[3])
    return rows, next_cursor, prev_cursor


# Функция для загрузки и отображения тикетов
async def show_tickets(texts, language='language:RU', current_position: int = 0):
    last_three_tickets, has_more = await take_tickets_for_support(current_position)

    if last_three_tickets is None:  # Выводим сообщение что тикетов больше нет, если запуск был через команду(т.е. на получение трёх старейших тикетов)
        return [(texts[language]['support_no_tickets'], None)], last_three_tickets, has_more
    else:  # Если есть - выводим их
        tickets = []
        for ticket in last_three_tickets:
            ticket_message = (
                f'Ticket_id: {ticket['id']}\n\nUser_id: {ticket['user_id']}'
                f'\n{ticket['send_time'].strftime("%Y-%m-%d %H:%M")}\n\n"{ticket['message']}"')
            tickets.append((ticket_message, await answer_to_ticket_kb(ticket['id'], ticket['user_id'],
                                                                      texts[language]['support_answer_bt'])))
        return tickets, last_three_tickets, has_more


# Функция для загрузки и отображения банов
async def show_bans(texts, language='language:RU', current_position: int = 0):
    last_three_bans, has_more = await take_bans(current_position)

    print(last_three_bans)
    if last_three_bans is None:  # Выводим сообщение что банов больше нет, если запуск был через команду(т.е. на получение трёх старейших банов)
        return [(texts[language]['no_bans'], None)], last_three_bans, has_more
    else:  # Если есть - выводим их
        bans = []
        for ban in last_three_bans:
            ban_message = (
                f'<b>Ban ID: {ban['id']}</b>\n\n<b>User ID</b>: {ban['user_id']}'
                f'\n<b>Admin ID:</b>{ban['banned_by']}\n<i>{ban['banned_at'].strftime("%Y-%m-%d %H:%M")}</i>\n\n<b>{texts[language]['reason']}</b>\n{ban['reason']}')
            bans.append((ban_message, await unban_user_kb(ban['user_id'], texts[language]['unban'])))
        return bans, last_three_bans, has_more
