import re
import sympy as sp
import numpy as np
import io
import matplotlib.pyplot as plt
from sympy import parse_expr
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication,
    convert_xor
)

ALLOWED_SYMBOLS = {'x', 'e', 'pi'}
transformations = standard_transformations + (implicit_multiplication, convert_xor)


# ---------------------------
# CLEAN
# ---------------------------
def clean_expression(expr: str) -> str:
    cleaned = expr.lower().replace(' ', '')

    replacements = {
        'ctan': 'cot',
        'cotan': 'cot',
        'tg': 'tan',
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
    func = match.group(1)
    value = np.radians(float(match.group(2)))
    return f"{func}({value})"


# ---------------------------
# PARSE CORE
# ---------------------------
def parse_expression(expr: str, evaluate: bool = True):
    expr = clean_expression(expr)

    expr = re.sub(
        r'(sin|cos|tan|cot)\((-?\d+(?:\.\d+)?)\)',
        replace_degrees,
        expr
    )

    parsed = parse_expr(
        expr,
        transformations=transformations,
        evaluate=evaluate
    )

    used = {s.name for s in parsed.free_symbols}
    invalid = used - ALLOWED_SYMBOLS
    if invalid:
        raise ValueError(f"Недопустимые переменные: {invalid}")

    return parsed.subs({'e': sp.E, 'pi': sp.pi})


# ---------------------------
# NUMPY FUNCTION (graph/eval)
# ---------------------------
def to_numpy_function(expr: str):
    parsed = parse_expression(expr, evaluate=False)
    return sp.lambdify("x", parsed, modules=["numpy"])


# ---------------------------
# EQUATION SOLVER
# ---------------------------
def solve_equation(expr: str):
    expr = clean_expression(expr)

    if "=" not in expr:
        raise ValueError("Нет '=' в уравнении")

    left, right = expr.split("=")

    x = sp.Symbol("x")

    eq = sp.Eq(
        parse_expression(left),
        parse_expression(right)
    )

    sol = sp.solve(eq, x)

    return "; ".join(
        f"x = {str(round(s, 3)).rstrip('0').rstrip('.') if isinstance(s, (int, float)) else s}"
        for s in sol
    )


# ---------------------------
# INEQUALITY SOLVER
# ---------------------------
def solve_inequality(expr: str):
    expr = clean_expression(expr)
    x = sp.Symbol("x")

    # поддержка вида x > 2x+1
    parsed = parse_expression(expr, evaluate=False)

    solution = sp.solve_univariate_inequality(parsed, x)

    return f"x ∈ {sp.pretty(solution, use_unicode=True)}"


# ---------------------------
# EVALUATE (простые примеры)
# ---------------------------
def evaluate_expression(expr: str):
    parsed = parse_expression(expr)
    result = float(parsed.evalf())

    return str(round(result, 3)).rstrip('0').rstrip('.')


# ---------------------------
# PLOT
# ---------------------------
def generate_plot(f_numpy, expr_str: str, user_language: str, x_range=(-10, 10)):
    if x_range[0] >= x_range[1]:
        raise ValueError("bad range")

    x = np.linspace(*x_range, 1000)

    with np.errstate(all='ignore'):
        y = f_numpy(x)

    y = np.ma.masked_invalid(y)
    y = np.ma.masked_where(np.abs(y) > 1e5, y)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x, y)

    ax.grid(True, linestyle="--", alpha=0.7)

    ax.set_xlim(x_range)

    if any(fn in expr_str for fn in ["sin", "cos", "tan", "cot"]):
        ax.set_ylim(-5, 5)

    title = "Plot" if user_language == "EN" else "График"
    ax.set_title(f"{title}: {expr_str}")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    return buf
