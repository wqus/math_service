import pytest
from bot.utils.utils import zamena

@pytest.mark.parametrize('input_str, expected', [
    ('sin(30)','sin(math.radians(30))'),
    ('sin(30)+cos(60)','sin(math.radians(30))+cos(math.radians(60))'),
    ('cos(x)','cos(x)'),
    ("sin(cos(30))","sin(cos(math.radians(30)))"),
    ("5+4x","5+4x"),
    ("",""),
])
def test_zamena(input_str, expected):
    assert zamena(input_str) == expected


def test_zamena(input_str, expected):
    assert zamena(input_str) == expected
