import re
import sympy as sp
import numpy as np
import io
import matplotlib.pyplot as plt
from sympy import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication, convert_xor

ALLOWED_SYMBOLS = {'x', 'e', 'pi'}
transformations = standard_transformations + (implicit_multiplication, convert_xor)


def clean_expression(expr: str) -> str:
    cleaned = expr.lower().replace(' ', '')

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

    if re.search(r'(__|import|lambda|eval|exec|system)', cleaned):
        raise ValueError("Недопустимые операции в выражении")
    return cleaned


def replace_degrees(match):
    func_name = match.group(1)
    degrees_to_radians = np.radians(int(match.group(2)))
    return f"{func_name}({degrees_to_radians})"


# Функция для решения уравнения
def solve_equation(user_input: str, inequality_type: str):
    # Заменяем символы для представления бесконечности
    user_input = user_input.replace('oo', 'sp.oo')

    # Разделяем неравенство на левую и правую части
    left, right = user_input.split(inequality_type)
    left_expr = sp.parse_expr(left)
    right_expr = sp.parse_expr(right)

    # Решаем уравнение
    solution = sp.solve(sp.Eq(left_expr, right_expr), sp.symbols('x'))

    # Преобразуем решение в красивую строку
    formatted_solution = sp.pretty(solution, use_unicode=True)
    return formatted_solution


def parse_expression(expr: str, evaluate: bool = True):
    cleaned = clean_expression(expr)
    cleaned = re.sub(r'(sin|cos|tan|cot)\((\d+)\)', replace_degrees, cleaned)
    # Парсинг выражения через SymPy
    try:
        parsed = parse_expr(cleaned, transformations=transformations, evaluate=evaluate)
    except Exception as e:
        if "cannot be used as a variable" in str(e):
            raise ValueError("Недопустимое имя функции или переменной")
        elif "invalid syntax" in str(e):
            raise ValueError("Синтаксическая ошибка в выражении")
        else:
            raise ValueError(f"Ошибка парсинга: {str(e)}")
    # Проверка допустимых переменных
    used_symbols = {s.name for s in parsed.free_symbols}
    invalid = used_symbols - ALLOWED_SYMBOLS
    if invalid:
        raise ValueError(f"Недопустимые переменные: {', '.join(invalid)}")

    # Замена e и pi на числовые значения
    parsed = parsed.subs({'e': sp.E, 'pi': sp.pi})
    return parsed


def safe_parse_to_numpy_answer(expr: str):
    return parse_expression(expr)


def safe_parse_to_numpy_function(expr: str):
    parsed = parse_expression(expr, evaluate=False)
    try:
        return sp.lambdify("x", parsed, modules=["numpy"])
    except Exception:
        raise ValueError("Невозможно преобразовать выражение в NumPy функцию")


# Функция генерации графика
def generate_plot(f_numpy, expr_str: str, user_language: str, x_range: tuple[float, float] = (-10, 10)) -> io.BytesIO:
    # Проверка корректности диапазона
    if x_range[1] <= x_range[0]:
        raise ValueError("Некорректный диапазон значений X")

    # Создаём массив точек
    x = np.linspace(x_range[0], x_range[1], 1000)

    # Вычисляем значения функции
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
