from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

# language buttons
russian_lan_bt = types.InlineKeyboardButton(text='Русский🇷🇺', callback_data='language:RU')
english_lan_bt = types.InlineKeyboardButton(text='English🇬🇧', callback_data='language:EN')
# user_language_kb
kb_language = types.InlineKeyboardMarkup(inline_keyboard=[[russian_lan_bt, english_lan_bt]])


async def payment_kb(user_language='language:RU', link1m='', link3m='', link12m=''):
    texts = {'language:RU': {"month1": "1 МЕСЯЦ", "months3": "3 МЕСЯЦА", "months12": "12 МЕСЯЦЕВ"},
             'language:EN': {"month1": "1 MONTH", "months3": "3 MONTHS", "months12": "12 MONTHS"}}
    # payment type bts
    month_1 = types.InlineKeyboardButton(text=texts[user_language]['month1'], callback_data="month1", url=link1m)
    months_3 = types.InlineKeyboardButton(text=texts[user_language]['months3'], callback_data="months3", url=link3m)
    months_12 = types.InlineKeyboardButton(text=texts[user_language]['months12'], callback_data="months12", url=link12m)

    return types.InlineKeyboardMarkup(inline_keyboard=[[month_1, months_3], [months_12]])


async def page_keyboard(next_cursor=None, prev_cursor=None):
    # Строим inline-клавиатуру для пагинации.
    builder = InlineKeyboardBuilder()

    if prev_cursor:
        cursor_str = f"user:history:prev:{prev_cursor[0]}|{prev_cursor[1]}"
        builder.button(text="⬅️", callback_data=cursor_str)

    if next_cursor:
        cursor_str = f"user:history:next:{next_cursor[0]}|{next_cursor[1]}"
        builder.button(text="➡️", callback_data=cursor_str)

    builder.adjust(2)
    return builder


# Клавиатура, чтобы отправлять запрос для ответа на тикет
async def answer_to_ticket_kb(ticket_id, user_id, answer_text):
    builder = InlineKeyboardBuilder()
    builder.button(text=answer_text, callback_data=f'admin:answer:{ticket_id}:{user_id}')

    return builder


# Клавиатура, чтобы отправлять запрос на вывод ещё трех запросов
async def load_three_tickets_kb(last_ticket_id, load_more_text):
    builder = InlineKeyboardBuilder()
    builder.button(text=load_more_text, callback_data=f'admin:load:{last_ticket_id}')

    return builder


# Клавиатура, чтобы оценивать ответ поддержик
async def rate_support_answer_kb(ticket_id):
    builder = InlineKeyboardBuilder()

    builder.button(text='1', callback_data=f'ticket:{ticket_id}:1')
    builder.button(text='2', callback_data=f'ticket:{ticket_id}:2')
    builder.button(text='3', callback_data=f'ticket:{ticket_id}:3')
    builder.button(text='4', callback_data=f'ticket:{ticket_id}:4')
    builder.button(text='5', callback_data=f'ticket:{ticket_id}:5')

    return builder
