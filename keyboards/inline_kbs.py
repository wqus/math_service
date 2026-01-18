from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

#language buttons
russian_lan_bt = types.InlineKeyboardButton(text='Русский🇷🇺', callback_data='language:RU')
english_lan_bt = types.InlineKeyboardButton(text='English🇬🇧', callback_data = 'language:EN')
# user_language_kb
kb_language = types.InlineKeyboardMarkup(inline_keyboard=[[russian_lan_bt, english_lan_bt]])

async def payment_kb(language = 'language:RU', link1m = '',link3m = '',link12m = ''):
    texts = {'language:RU': {"month1" : "1 МЕСЯЦ", "months3" : "3 МЕСЯЦА","months12" : "12 МЕСЯЦЕВ"},
             'language:EN': {"month1" : "1 MONTH", "months3" : "3 MONTHS","months12" : "12 MONTHS"}}
    #payment type bts
    month_1 = types.InlineKeyboardButton(text=texts[language]['month1'], callback_data="month1", url = link1m)
    months_3 = types.InlineKeyboardButton(text=texts[language]['months3'], callback_data="months3", url = link3m)
    months_12 = types.InlineKeyboardButton(text=texts[language]['months12'], callback_data="months12", url = link12m)

    return types.InlineKeyboardMarkup(inline_keyboard=[[month_1,months_3],[months_12]])

async def page_keyboard(next_cursor=None, prev_cursor=None):
    logger = logging.getLogger(__name__)
    logger.info("Создание/обновление клавиатуры для историй")
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

