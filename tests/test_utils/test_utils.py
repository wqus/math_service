import pytest
import re
from io import BytesIO
import sympy as sp
from sympy import oo, Interval, Union, FiniteSet

from bot.utils.utils import (
    evaluate_expression,
    solve_inequality,
    generate_plot,
    to_numpy_function,
    solve_equation,
    format_output,
    pretty_number,
    parse_inequality
)


# EXPRESSIONS
@pytest.mark.parametrize("expr,expected", [
    ("1+1", "2"),
    ("2*2", "4"),
    ("3+5", "8"),
    ("10/2", "5"),
    ("2**3", "8"),
    ("sqrt(16)", "4"),
    ("sin(pi/2)", "1"),
    ("cos(0)", "1"),
    ("tan(pi/4)", "1"),
])
def test_evaluate_expression_calculates_correctly(expr, expected):
    result = evaluate_expression(expr)
    if '.' not in expected:
        assert result == expected
    else:
        assert abs(float(result) - float(expected)) < 0.01


# EQUATIONS
@pytest.mark.parametrize("expr,expected_contains", [
    ("x+2=5", "x = 3"),
    ("2*x=10", "x = 5"),
    ("x**2=4", "x = -2"),
    ("x**2=4", "x = 2"),
])
def test_solve_equation(expr, expected_contains):
    result = solve_equation(expr)
    assert expected_contains in result


def test_solve_equation_multiple_solutions():
    result = solve_equation("x**2-9=0")
    assert "x = -3" in result
    assert "x = 3" in result


@pytest.mark.parametrize("expr", [
    ("x+y=5"),
    ("=5"),
    ("no equal sign"),
])
def test_solve_equation_invalid(expr):
    with pytest.raises(Exception):
        solve_equation(expr)


# INEQUALITIES
@pytest.mark.parametrize("expr,expected_contains", [
    ("x > 2", "(2, ∞)"),
    ("x < -1", "(-∞, -1)"),
    ("x >= 0", "[0,"),
    ("x <= 5", ", 5]"),
    ("x**2 > 4", "(-∞, -2)"),
    ("x**2 > 4", "(2, ∞)"),
    ("x**2 < 9", "(-3, 3)"),
])
def test_solve_inequality(expr, expected_contains):
    result = solve_inequality(expr)
    assert expected_contains in result


@pytest.mark.parametrize("expr", [
    ("x + 2"),
    ("x = 5"),
])
def test_solve_inequality_invalid(expr):
    with pytest.raises(Exception):
        solve_inequality(expr)


# PLOT
def test_generate_plot_valid():
    f = to_numpy_function("x**2")
    buf = generate_plot(f, "x**2", "EN", (-5, 5))
    assert isinstance(buf, BytesIO)
    assert buf.getbuffer().nbytes > 0


def test_generate_plot_with_trigonometric():
    f = to_numpy_function("sin(x)")
    buf = generate_plot(f, "sin(x)", "RU", (-10, 10))
    assert isinstance(buf, BytesIO)
    assert buf.getbuffer().nbytes > 0


@pytest.mark.parametrize("bad_range", [
    (5, 5),
    (10, 1),
    (0, -1),
])
def test_generate_plot_invalid_range(bad_range):
    f = to_numpy_function("x")
    with pytest.raises(ValueError, match="bad range"):
        generate_plot(f, "x", "EN", bad_range)


# FORMAT OUTPUT
@pytest.mark.parametrize("value,expected", [
    (sp.Rational(1, 2), "0.5"),
    (sp.Rational(2, 1), "2"),
    (sp.Integer(42), "42"),
    (sp.Float(3.14159), "3.142"),
    (sp.Float(1.0), "1"),
    (1.5, "1.5"),
    (2.0, "2"),
])
def test_pretty_number(value, expected):
    result = pretty_number(value)
    assert result == expected


def test_pretty_number_with_numpy():
    import numpy as np
    assert pretty_number(np.float64(3.14159)) == "3.142"
    assert pretty_number(np.float64(2.0)) == "2"


def test_format_output_interval():
    from sympy import Interval, oo

    # Закрытый интервал
    result = format_output(Interval(0, 5))
    assert result == "[0, 5]"

    # Открытый интервал
    result = format_output(Interval(0, 5, left_open=True, right_open=True))
    assert result == "(0, 5)"

    # Бесконечность
    result = format_output(Interval(0, oo))
    assert result == "[0, ∞)"

    result = format_output(Interval(-oo, 0))
    assert result == "(-∞, 0]"


def test_format_output_number():
    result = format_output(sp.Integer(42))
    assert result == "42"

    result = format_output(sp.Rational(1, 3))
    assert "0.333" in result


# PARSE INEQUALITY
def test_parse_inequality():
    result = parse_inequality("x > 5")
    assert isinstance(result, sp.GreaterThan) or isinstance(result, sp.StrictGreaterThan)

    result = parse_inequality("x >= 5")
    assert isinstance(result, sp.GreaterThan)

    result = parse_inequality("x < 5")
    assert isinstance(result, sp.LessThan) or isinstance(result, sp.StrictLessThan)


def test_parse_inequality_invalid():
    with pytest.raises(ValueError):
        parse_inequality("x + 5")

    with pytest.raises(ValueError):
        parse_inequality("x = 5")


# NUMPY FUNCTION
def test_to_numpy_function():
    f = to_numpy_function("x**2 + 3*x + 1")
    import numpy as np
    x = np.array([0, 1, 2])
    result = f(x)
    expected = np.array([1, 5, 11])
    np.testing.assert_array_almost_equal(result, expected)


def test_to_numpy_function_trigonometric():
    f = to_numpy_function("sin(x)")
    import numpy as np
    result = f(np.pi / 2)
    assert abs(result - 1.0) < 0.0001


# EDGE CASES
def test_evaluate_expression_with_constants():
    assert evaluate_expression("pi") == "3.142"
    assert evaluate_expression("e") == "2.718"


def test_solve_inequality_no_solution():
    result = solve_inequality("x**2 < -1")
    assert result is not None


def test_pretty_number_edge():
    assert pretty_number(0) == "0"
    assert pretty_number(-0) == "0"
    assert pretty_number(1e-10) == "0"
