from aiogram import types
from startup import texts
# KEY BOARDS
#REPLY_KBs
kb_info = {
    'RU': types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text = texts['RU']['skills']), types.KeyboardButton(text = texts['RU']['note'])], [types.KeyboardButton(text = texts['RU']['plot'])]],resize_keyboard=True),
    'EN': types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text = texts['EN']['skills']), types.KeyboardButton(text = texts['EN']['note'])], [types.KeyboardButton(text = texts['EN']['plot'])]],resize_keyboard=True)
}
