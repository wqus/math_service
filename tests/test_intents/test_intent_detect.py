from bot.intents.intent_detect import detect_intent
from bot.intents.Intent import Intent


def test_detect_intent_math():
    assert detect_intent("Правила", "language:RU") == Intent.RULES


def test_detect_intent_payments():
    assert detect_intent("Premium", "language:EN") == Intent.PAYMENTS


def test_detect_intent_unknown():
    assert detect_intent("Как дела?", "language:RU") == Intent.UNKNOWN
