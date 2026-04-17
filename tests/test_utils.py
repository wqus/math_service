import pytest
from bot.utils.utils import zamena

def test_zamena():
    assert zamena('sin(30)') == 'sin(math.radians(30))'