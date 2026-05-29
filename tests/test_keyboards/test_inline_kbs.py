import pytest

from bot.keyboards.inline_kbs import (
    payment_kb,
    page_keyboard,
    answer_to_ticket_kb,
    load_three_tickets_kb,
    load_three_bans_kb,
    rate_support_answer_kb,
    unban_user_kb,
    ai_functions_kb,
    kb_language,
    russian_lan_bt,
    english_lan_bt
)


def test_kb_language_buttons_text_and_callbacks():
    buttons = kb_language.inline_keyboard[0]

    assert buttons[0].text == "Русский🇷🇺"
    assert buttons[0].callback_data == "language:RU"

    assert buttons[1].text == "English🇬🇧"
    assert buttons[1].callback_data == "language:EN"


@pytest.mark.asyncio
@pytest.mark.parametrize("user_language,expected_texts", [
    ("language:RU", ["1 МЕСЯЦ", "3 МЕСЯЦА", "12 МЕСЯЦЕВ"]),
    ("language:EN", ["1 MONTH", "3 MONTHS", "12 MONTHS"]),
])
async def test_payment_kb_texts_by_language(user_language, expected_texts):
    kb = await payment_kb(
        user_language=user_language,
        link1m="http://test1.com",
        link3m="http://test3.com",
        link12m="http://test12.com"
    )

    assert kb.inline_keyboard[0][0].text == expected_texts[0]
    assert kb.inline_keyboard[0][1].text == expected_texts[1]

    assert kb.inline_keyboard[1][0].text == expected_texts[2]


# Тесты для пагинации
@pytest.mark.asyncio
async def test_page_keyboard_both_cursors():
    next_cursor = ("field1", "value1")
    prev_cursor = ("field2", "value2")

    kb = await page_keyboard(next_cursor=next_cursor, prev_cursor=prev_cursor)

    markup = kb.as_markup()  # InlineKeyboardMarkup
    buttons = markup.inline_keyboard[0]

    assert len(buttons) == 2
    assert buttons[0].text == "⬅️"
    assert buttons[0].callback_data == f"user:history:prev:{prev_cursor[0]}|{prev_cursor[1]}"
    assert buttons[1].text == "➡️"
    assert buttons[1].callback_data == f"user:history:next:{next_cursor[0]}|{next_cursor[1]}"


@pytest.mark.asyncio
async def test_page_keyboard_only_next():
    next_cursor = ("page", "2")

    kb = await page_keyboard(next_cursor=next_cursor, prev_cursor=None)
    markup = kb.as_markup()
    buttons = markup.inline_keyboard[0]

    assert len(buttons) == 1
    assert buttons[0].text == "➡️"


@pytest.mark.asyncio
async def test_answer_to_ticket_kb_callback_format():
    kb = await answer_to_ticket_kb(123, 456, "Ответить")
    markup = kb.as_markup()
    button = markup.inline_keyboard[0][0]

    assert button.callback_data == "admin:answer:123:456"
    assert button.text == "Ответить"
