import re
import io
import sympy as sp
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sympy import parse_expr
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication,
    convert_xor
)

from sympy import Interval, Union, FiniteSet, oo
from sympy.core.relational import Relational


# CONFIG

ALLOWED_SYMBOLS = {"x", "e", "pi"}

transformations = standard_transformations + (
    implicit_multiplication,
    convert_xor
)


# PRETTY OUTPUT

def pretty_number(x):
    if isinstance(x, sp.Basic) and x.is_Number:
        x = float(x.evalf())

    elif isinstance(x, (int, float, np.integer, np.floating)):
        x = float(x)

    else:
        return str(x)

    if abs(x - round(x)) < 1e-10:
        return str(int(round(x)))

    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def pretty_expr(expr):
    expr = sp.simplify(expr)

    if expr.is_Number:
        return pretty_number(expr)

    return str(expr)


def pretty_interval(interval):
    if interval == sp.S.Reals:
        return "(-∞, ∞)"

    def fmt(v):
        if v == -oo:
            return "-∞"
        if v == oo:
            return "∞"
        return pretty_number(v)

    left = fmt(interval.start)
    right = fmt(interval.end)

    lb = "(" if interval.left_open else "["
    rb = ")" if interval.right_open else "]"

    return f"{lb}{left}, {right}{rb}"


def format_output(result):
    if result == sp.S.EmptySet:
        return "∅"

    if isinstance(result, Interval):
        return pretty_interval(result)

    if isinstance(result, Union):
        return " ∪ ".join(format_output(a) for a in result.args)

    if isinstance(result, FiniteSet):
        return "{%s}" % ", ".join(format_output(a) for a in result)

    if isinstance(result, list):
        return "; ".join(format_output(a) for a in result)

    if isinstance(result, sp.Basic):
        return pretty_expr(result)

    return str(result)


# CLEANING
def clean_expression(expr: str):
    cleaned = expr.lower().replace(" ", "")

    replacements = {
        "ctan": "cot",
        "cotan": "cot",
        "tg": "tan",
        "cosec": "csc",
        "secant": "sec",
        "²": "**2",
        "³": "**3",
        "^": "**"
    }

    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    if re.search(r"(__|import|lambda|eval|exec|system)", cleaned):
        raise ValueError("Недопустимые операции")

    return cleaned


# PARSING
def parse_expression(expr: str, evaluate=True):
    expr = clean_expression(expr)

    parsed = parse_expr(
        expr,
        transformations=transformations,
        evaluate=evaluate
    )

    used = {s.name for s in parsed.free_symbols}
    invalid = used - ALLOWED_SYMBOLS

    if invalid:
        raise ValueError(f"Недопустимые переменные: {invalid}")

    return parsed.subs({"e": sp.E, "pi": sp.pi})


def parse_inequality(expr: str):
    expr = clean_expression(expr)

    try:
        parsed = parse_expr(
            expr,
            transformations=transformations,
            evaluate=False
        )
    except Exception:
        raise ValueError("Некорректное неравенство")

    if not isinstance(parsed, Relational):
        raise ValueError("Не неравенство")

    return parsed



# EQUATIONS

def solve_equation(expr: str):
    if "=" not in expr:
        raise ValueError("Нет '='")

    left, right = expr.split("=")

    x = sp.Symbol("x")

    eq = sp.Eq(parse_expression(left), parse_expression(right))
    sol = sp.solve(eq, x)

    if not sol:
        return ""

    return "; ".join(f"x = {format_output(s)}" for s in sol)


# INEQUALITIES
def solve_inequality(expr: str):
    x = sp.Symbol("x")
    ineq = parse_inequality(expr)

    solution = sp.solve_univariate_inequality(
        ineq,
        x,
        relational=False
    )

    return f"x ∈ {format_output(solution)}"



# CALCULATOR
def evaluate_expression(expr: str):
    parsed = parse_expression(expr)
    result = parsed.evalf()
    return pretty_number(result)


def to_numpy_function(expr: str):
    parsed = parse_expression(expr, evaluate=False)
    return sp.lambdify("x", parsed, modules=["numpy"])


# PLOT
def generate_plot(f_numpy, expr_str, user_language, x_range=(-10, 10)):
    if x_range[0] >= x_range[1]:
        raise ValueError("bad range")

    x = np.linspace(*x_range, 1000)

    with np.errstate(all="ignore"):
        y = f_numpy(x)

    y = np.ma.masked_invalid(y)
    y = np.ma.masked_where(np.abs(y) > 1e5, y)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x, y)

    ax.grid(True, linestyle="--", alpha=0.7)
    ax.set_xlim(x_range)

    if any(fn in expr_str for fn in ("sin", "cos", "tan", "cot")):
        ax.set_ylim(-5, 5)

    title = "Plot" if user_language == "EN" else "График"
    ax.set_title(f"{title}: {expr_str}")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)

    buf.seek(0)
    return buf
