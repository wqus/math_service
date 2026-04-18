import pytest
from bot.utils.utils import clean_expression, replace_degrees, solve_equation, parse_expression, \
    safe_parse_to_numpy_answer, safe_parse_to_numpy_function, generate_plot

#clean_expression
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

#replace_degrees
@pytest.mark.parametrize("expr", [
    "sin(90)",
    "cos(180)",
    "tan(45)",
])
def test_replace_degrees(expr):
    assert replace_degrees(expr)

#solve_equation
def test_solve_equation():
    assert clean_expression(inp) == expected


#parse_expression
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
    "2..5",
    "invalid!!!"
])
def test_parse_expression_invalid_variables(bad):
    with pytest.raises(ValueError):
        parse_expression(bad)

#safe_parse_to_numpy_answer
def test_safe_parse_to_numpy_answer():
    assert clean_expression(inp) == expected

#safe_parse_to_numpy_function
def test_safe_parse_to_numpy_function():
    assert clean_expression(inp) == expected

#generate_plot
def test_generate_plot():
    assert clean_expression(inp) == expected
