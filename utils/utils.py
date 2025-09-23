import re
import sympy as sp
import numpy as np
import io
import matplotlib.pyplot as plt
from Scripts.activate_this import prev_length
from sympy import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication, convert_xor
import aiosqlite

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

x_range = (-10,10)
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
    async with aiosqlite.connect('users_history.db') as conn:
        await conn.execute('INSERT INTO history(user_id, input_message, output_message)'
                     'VALUES (?, ?, ?)', (user_id, input_message, output_message))
        await conn.commit()
        await conn.close()


async def requests_history(user_id, cursor=None, page_size=10, direction="next"):
    query = "SELECT id, input_message, output_message, created_at FROM history WHERE user_id = ?"
    values = [user_id]

    # курсорная навигация
    if cursor:
        print(f"CURSOR: {cursor}")
        cursor_id, cursor_created_at = cursor
        if direction == "next":
            query += " AND (created_at < ? OR (created_at = ? AND id < ?))"
        elif direction == "prev":
            query += " AND (created_at > ? OR (created_at = ? AND id > ?))"
        values.extend([cursor_created_at, cursor_created_at, cursor_id])

    if direction == "prev":
        query += " ORDER BY created_at, id LIMIT ?"
    else: query += " ORDER BY created_at DESC, id DESC LIMIT ?"
    values.append(page_size)

    async with aiosqlite.connect("users_history.db") as conn:
        conn.row_factory = aiosqlite.Row
        rows = await conn.execute_fetchall(query, values)
        for row in rows:
            print(row["input_message"])

    prev_cursor, next_cursor = None, None

    if rows:
        if direction == "prev":
            first = rows[-1]
            last = rows[0]
        elif direction == "next":
            first = rows[0]
            last = rows[-1]

        async with aiosqlite.connect("users_history.db") as conn:
            conn.row_factory = aiosqlite.Row

            # проверяем наличие записей новее (для prev-кнопки)
            newer = await conn.execute_fetchall(
                """
                SELECT 1 FROM history
                WHERE user_id = ?
                  AND (created_at > ? OR (created_at = ? AND id > ?))
                LIMIT 1
                """,
                (user_id, first["created_at"], first["created_at"], first["id"])
            )
            if newer:
                prev_cursor = (first["id"], first["created_at"])
                print(f"newer updated: {prev_cursor}")

            # проверяем наличие записей старее (для next-кнопки)
            older = await conn.execute_fetchall(
                """
                SELECT 1 FROM history
                WHERE user_id = ?
                  AND (created_at < ? OR (created_at = ? AND id < ?))
                LIMIT 1
                """,
                (user_id, last["created_at"], last["created_at"], last["id"])
            )
            if older:
                next_cursor = (last["id"], last["created_at"])

    return rows, next_cursor, prev_cursor