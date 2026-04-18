import pytest
from bot.utils.utils import clean_expression, solve_equation, parse_expression, safe_parse_to_numpy_function, generate_plot
import numpy as np
import io


# clean_expression
@pytest.mark.parametrize("inp,expected", [
    ("TG(x)", "tan(x)"),
    ("ctan(x)", "cot(x)"),
    ("x^2", "x**2"),
    ("x²", "x**2"),
    ("x+7", "x+7"),
    ("", "")
])
def test_clean_expression(inp, expected):
    assert clean_expression(inp) == expected


@pytest.mark.parametrize("bad", [
    "__import__('os')",
    "eval('2+2')",
    "exec('print(1)')",
    "lambda x: x",
    "system('ls')",
])
def test_security_clean_expression(bad):
    with pytest.raises(ValueError):
        clean_expression(bad)


# solve_equation
@pytest.mark.parametrize('equation, expected_solution', [
    ("x + 2 = 5", "[3]"),
    ("x - 3 = 0", "[3]"),
    ("2*x = 10", "[5]"),
    ("x**2 = 9", "[-3, 3]"),
    ("x**2 = 0", "[0]"),
    ("x + 1 = x", "[]")
])
def test_solve_equation(equation, expected_solution):
    result = solve_equation(equation)
    if expected_solution == "[-3, 3]":
        assert result in ["[-3, 3]", "[3, -3]"]
    else:
        assert result == expected_solution


# parse_expression
@pytest.mark.parametrize("expr,expected_value", [
    ("2+2", 4),
    ("sin(0)", 0),
    ("cos(0)", 1),
])
def test_parse_expression_calculates_correctly(expr, expected_value):
    assert parse_expression(expr) == expected_value


@pytest.mark.parametrize("bad", [
    "y",
    "z",
    "t",
    "x+y",
    "sin(,)",
    "invalid!!!"
])
def test_parse_expression_invalid_variables(bad):
    with pytest.raises(ValueError):
        parse_expression(bad)

# safe_parse_to_numpy_function
def test_safe_parse_to_numpy_function():
    f = safe_parse_to_numpy_function("x**2")
    x_values = np.array([-2, -1, 0, 1, 2])
    result = f(x_values)

    assert np.all(result == [4, 1, 0, 1, 4])

# generate_plot
def test_generate_plot():
    f = safe_parse_to_numpy_function('x**2')
    result = generate_plot(f, "x**2", 'RU')

    assert isinstance(result, io.BytesIO)
    assert result.getbuffer().nbytes > 0


@pytest.mark.parametrize('bad_range', [
    (10, -10),
    (0, 0),
    (5, 1)
])
def test_generate_plot_invalid_range(bad_range):
    f = safe_parse_to_numpy_function("x**2")
    with pytest.raises(ValueError, match="Некорректный диапазон"):
        generate_plot(f, 'x**2', 'RU', bad_range)

