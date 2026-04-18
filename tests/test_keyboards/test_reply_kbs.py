from bot.keyboards.reply_kbs import kb_info
import pytest
from aiogram import types


@pytest.mark.asyncio()
async def test_kb_info():
    print("KB TEST RUNNING")

    language = 'language:EN'
    texts = {
        "language:EN": {
            "skills": "Skills",
            "note": "Note",
            "support": "Support",
            "history": "History",
            "plot": "Plot",
            "premium": "Premium"
        }
    }
    kb = await kb_info(texts, language)
    assert isinstance(kb, types.ReplyKeyboardMarkup)
    assert len(kb.keyboard) == 4
    assert len(kb.keyboard[0]) == 2
    assert len(kb.keyboard[1]) == 2
    assert len(kb.keyboard[2]) == 1
    assert len(kb.keyboard[3]) == 1
