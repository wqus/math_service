from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
#INLINE_BTs
#language buttons
russian_lan_bt = types.InlineKeyboardButton(text='Русский🇷🇺', callback_data='language:RU')
english_lan_bt = types.InlineKeyboardButton(text='English🇬🇧', callback_data = 'language:EN')

# INLINE_KBs
kb_language = types.InlineKeyboardMarkup(inline_keyboard=[[russian_lan_bt, english_lan_bt]])

async def page_keyboard(next_cursor=None, prev_cursor=None):
    #Строим inline-клавиатуру для пагинации.
    builder = InlineKeyboardBuilder()

    if prev_cursor:
        cursor_str = f"user:history:prev:{prev_cursor[0]}|{prev_cursor[1]}"
        builder.button(text="⬅️", callback_data=cursor_str)

    if next_cursor:
        cursor_str = f"user:history:next:{next_cursor[0]}|{next_cursor[1]}"
        builder.button(text="➡️", callback_data=cursor_str)

    builder.adjust(2)
    return builder
